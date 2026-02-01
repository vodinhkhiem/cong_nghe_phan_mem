import unittest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

class TestAuthUserFlow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Khác với Kanban (Mock Auth), ở đây ta test Auth thật 
        nên KHÔNG mock middleware. Ta cần test luồng sinh Token và check Password thật.
        """
        print("\n=== SETUP: Khởi tạo Test Auth ===")
        
        # Import App thật
        from app import create_app
        from infrastructure.databases.mssql import SessionLocal
        from infrastructure.models.user_model import UserModel
        
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()
        
        # Xóa user test cũ nếu có (tránh trùng email)
        session = SessionLocal()
        try:
            user = session.query(UserModel).filter_by(email="test_auth@example.com").first()
            if user:
                session.delete(user)
                session.commit()
                print("⚠️ Đã xóa user test cũ để dọn dẹp.")
        finally:
            session.close()

    def test_auth_lifecycle(self):
        print("\n=== BẮT ĐẦU TEST AUTHENTICATION & USER ===")
        
        email = "test_auth@example.com"
        password = "Password123!"

        # 1. ĐĂNG KÝ (REGISTER)
        payload_reg = {
            "full_name": "Test Auth User",
            "email": email,
            "password": password,
            "role": "Student"
        }
        res = self.client.post('/api/v1/auth/register', json=payload_reg)
        self.assertEqual(res.status_code, 201, f"Lỗi đăng ký: {res.get_data(as_text=True)}")
        print("✅ [1] Register Success")

        # 2. ĐĂNG NHẬP (LOGIN)
        payload_login = {
            "email": email,
            "password": password
        }
        res = self.client.post('/api/v1/auth/login', json=payload_login)
        self.assertEqual(res.status_code, 200)
        data = res.json
        
        # Kiểm tra response có đủ token không
        self.assertIn('accessToken', data)
        self.assertIn('refreshToken', data)
        self.assertIn('user', data)
        
        access_token = data['accessToken']
        refresh_token = data['refreshToken']
        print("✅ [2] Login Success & Got Tokens")

        # Header dùng cho các request sau
        headers = {'Authorization': f'Bearer {access_token}'}

        # 3. LẤY THÔNG TIN CÁ NHÂN (GET PROFILE)
        res = self.client.get('/api/v1/users/profile', headers=headers)
        if res.status_code != 200:
            print(f"\n❌ [DEBUG ERROR] Body: {res.get_data(as_text=True)}\n")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['email'], email)
        print("✅ [3] Get Profile Success (Token valid)")

        # 4. ĐỔI THÔNG TIN (UPDATE PROFILE)
        payload_update = {"description": "Updated via Unit Test"}
        res = self.client.put('/api/v1/users/profile', headers=headers, json=payload_update)
        self.assertEqual(res.status_code, 200)
        
        # Verify lại
        res = self.client.get('/api/v1/users/profile', headers=headers)
        self.assertEqual(res.json['description'], "Updated via Unit Test")
        print("✅ [4] Update Profile Success")

        # 5. REFRESH TOKEN
        res = self.client.post('/api/v1/auth/refresh-token', json={"refreshToken": refresh_token})
        self.assertEqual(res.status_code, 200)
        new_access_token = res.json['accessToken']
        self.assertNotEqual(new_access_token, access_token) # Token mới phải khác token cũ
        print("✅ [5] Refresh Token Success")

        # 6. ĐĂNG XUẤT (LOGOUT)
        # Dùng token mới để logout
        headers_new = {'Authorization': f'Bearer {new_access_token}'}
        res = self.client.post('/api/v1/auth/logout', headers=headers_new)
        self.assertEqual(res.status_code, 200)
        print("✅ [6] Logout Success")

        # 7. KIỂM TRA CHẶN TOKEN (SECURITY CHECK)
        # Thử dùng token vừa logout để lấy profile -> Phải bị lỗi 401
        res = self.client.get('/api/v1/users/profile', headers=headers_new)
        self.assertEqual(res.status_code, 401, "Token đã logout nhưng vẫn dùng được! (Lỗi bảo mật)")
        print("✅ [7] Security Check: Revoked Token is blocked")

if __name__ == '__main__':
    unittest.main()