import unittest
import sys
import os
import json

# Cấu hình đường dẫn
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from app import create_app
from infrastructure.databases.mssql import SessionLocal
from infrastructure.models.user_model import UserModel
from infrastructure.models.academic_model import SubjectModel, ClassModel

class TestCurriculumFlow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Chạy 1 lần trước khi test: Khởi tạo App, DB và Dữ liệu mẫu"""
        print("\n=== SETUP: Khởi tạo Test Curriculum ===")
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()
        cls.session = SessionLocal()

        # 1. Tạo Giảng viên & Sinh viên
        lec = cls.create_test_user("teacher_curr@test.com", "Lecturer")
        cls.lecturer_id = lec.id 
        
        stu = cls.create_test_user("student_curr@test.com", "Student")
        cls.student_id = stu.id   

        # 2. Tạo Môn học
        subject = cls.get_or_create(SubjectModel, code="TEST_SUB_CURR", name="Curriculum Test Subject")
        cls.subject_id = subject.id 

        # 3. Tạo Lớp học
        clazz = cls.get_or_create(ClassModel, 
                                  name="TEST_CLASS_CURR", 
                                  subject_id=cls.subject_id, 
                                  lecturer_id=cls.lecturer_id,
                                  semester="Spring 2026")
        cls.class_id = clazz.id    

        cls.session.commit()

        # 4. Lấy Token
        cls.token_lec = cls.login_user("teacher_curr@test.com")
        cls.token_stu = cls.login_user("student_curr@test.com")

        print("✅ Setup Data & Auth Tokens Complete!")

    @classmethod
    def tearDownClass(cls):
        cls.session.close()

    # --- HELPER FUNCTIONS ---
    @classmethod
    def get_or_create(cls, model, **kwargs):
        instance = cls.session.query(model).filter_by(**kwargs).first()
        if not instance:
            instance = model(**kwargs)
            cls.session.add(instance)
            cls.session.commit()
            cls.session.refresh(instance)
        return instance

    @classmethod
    def create_test_user(cls, email, role):
        user = cls.session.query(UserModel).filter_by(email=email).first()
        if not user:
            import bcrypt
            hashed = bcrypt.hashpw("123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user = UserModel(email=email, full_name="Test User", password=hashed, role=role, status=True)
            cls.session.add(user)
            cls.session.commit()
            cls.session.refresh(user)
        return user

    @classmethod
    def login_user(cls, email):
        res = cls.client.post('/api/v1/auth/login', json={"email": email, "password": "123"})
        return res.json['accessToken']

    # BẮT ĐẦU TEST CASES
    def test_01_get_current_semester(self):
        """Test 1: Lấy thông tin học kỳ hiện tại"""
        print("\n--- TEST 1: Get Current Semester ---")
        res = self.client.get('/api/v1/semesters/current')
        
        self.assertEqual(res.status_code, 200)
        data = res.json
        print(f"   Response: {data}")
        self.assertIn("name", data)
        self.assertTrue(data["is_active"])

    def test_02_update_syllabus(self):
        """Test 2: Giảng viên cập nhật Syllabus"""
        print("\n--- TEST 2: Update Syllabus ---")
        headers = {'Authorization': f'Bearer {self.token_lec}'}
        
        payload = {
            "content": "Nội dung đề cương cập nhật mới nhất 2026.",
            "clos": ["CLO1: Hiểu về Clean Arch", "CLO2: Viết được Unit Test"],
            "grading_scheme": {
                "Assignment": 30,
                "Project": 40,
                "Final Exam": 30
            }
        }
        
        res = self.client.put(f'/api/v1/syllabus/{self.class_id}', headers=headers, json=payload)
        
        if res.status_code != 200:
            print(f"❌ Error: {res.get_data(as_text=True)}")

        self.assertEqual(res.status_code, 200)
        print("   [OK] Syllabus Updated Successfully")

    def test_03_create_and_get_rubrics(self):
        """Test 3: Tạo và Lấy danh sách Rubric"""
        print("\n--- TEST 3: Manage Rubrics ---")
        headers = {'Authorization': f'Bearer {self.token_lec}'}

        # Đặt tên title đơn giản không dấu để tránh lỗi encoding khi so sánh (nếu DB chưa config utf8)
        test_title = "Rubric Python Code Test"
        
        payload = {
            "title": test_title,
            "description": "Tiêu chí chấm code clean",
            "content": [
                {"criteria": "Coding Style", "weight": 20},
                {"criteria": "Logic", "weight": 80}
            ]
        }
        
        # A. Tạo
        res_post = self.client.post('/api/v1/rubrics', headers=headers, json=payload)
        self.assertEqual(res_post.status_code, 201)
        print("   [A] Create Rubric: OK")

        # B. Lấy danh sách
        res_get = self.client.get('/api/v1/rubrics', headers=headers)
        self.assertEqual(res_get.status_code, 200)
        data = res_get.json
        
        print(f"   [B] Get Rubrics: Found {len(data)} items")
        
        # Debug: In ra các title tìm thấy
        found_titles = [r['title'] for r in data]
        print(f"       Titles found: {found_titles}")

        found = any(r['title'] == test_title for r in data)
        self.assertTrue(found, f"Không tìm thấy '{test_title}' trong danh sách!")

    def test_04_permission_check(self):
        """Test 4: Check quyền Sinh viên (403)"""
        print("\n--- TEST 4: Permission Check (Student) ---")
        headers = {'Authorization': f'Bearer {self.token_stu}'}
        
        res = self.client.put(f'/api/v1/syllabus/{self.class_id}', headers=headers, json={})
        
        self.assertEqual(res.status_code, 403)
        print("   [OK] Student blocked correctly (403 Forbidden)")

if __name__ == '__main__':
    unittest.main()