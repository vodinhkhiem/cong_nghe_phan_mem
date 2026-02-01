import unittest
import sys
import os
from unittest.mock import patch
from functools import wraps

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

class TestKanbanFlow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Chiến thuật: "Patch trước - Import sau"
        """
        print("\n=== SETUP: Bắt đầu vá lỗ hổng Auth ===")

        # 1. BẮT ĐẦU MOCK (GIẢ MẠO) AUTH MIDDLEWARE
        cls.auth_patcher = patch('api.middleware.auth_required')
        cls.mock_auth = cls.auth_patcher.start()

        # 2. ĐỊNH NGHĨA HÀM GIẢ
        def mock_decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                from flask import g
                g.user_id = 1  
                return f(*args, **kwargs)
            return wrapper
        
        # Gán hàm giả vào chỗ hàm thật
        cls.mock_auth.side_effect = mock_decorator
        print("✅ Auth đã được Mock thành công (User ID = 1)")

        # 3. BÂY GIỜ MỚI IMPORT APP (Lazy Import)
        from app import create_app 
        
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()
        
        cls.project_id = 1
        cls.headers = {'Content-Type': 'application/json'}

    @classmethod
    def tearDownClass(cls):
        cls.auth_patcher.stop()

    def test_kanban_full_lifecycle(self):
        print("\n=== BẮT ĐẦU TEST KANBAN ===")

        # [BƯỚC 1] TẠO TASK
        payload = {
            "title": "Task Lazy Import Fix",
            "description": "Test fix import order",
            "workspace_id": self.project_id,
            "status": "To Do",
            "priority": "High"
        }
        res = self.client.post('/api/v1/tasks/', headers=self.headers, json=payload)
        
        if res.status_code == 401:
            print("❌ VẪN LỖI 401: Bạn chưa xóa dòng 'from app import...' ở đầu file test!")
            
        self.assertEqual(res.status_code, 201, f"Lỗi tạo task: {res.get_data(as_text=True)}")
        task_id = res.json['id']
        print(f"✅ [1] Created Task ID: {task_id}")

        # [BƯỚC 2] DI CHUYỂN TASK
        move_payload = {"targetColumnId": "In Progress", "newPosition": 0}
        res = self.client.put(f'/api/v1/tasks/{task_id}/move', headers=self.headers, json=move_payload)
        self.assertEqual(res.status_code, 200)
        print(f"✅ [2] Moved Task to In Progress")

        # [BƯỚC 3] CHECKLIST
        res = self.client.post(f'/api/v1/tasks/{task_id}/checklist', headers=self.headers, json={"content": "Check Item"})
        self.assertEqual(res.status_code, 201)
        checklist_id = res.json['id']

        res = self.client.put(f'/api/v1/tasks/checklist/{checklist_id}/toggle', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        print(f"✅ [3] Checklist Added & Toggled")

        # [BƯỚC 4] VERIFY BOARD
        res = self.client.get(f'/api/v1/tasks/project/{self.project_id}/board', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        
        board_data = res.json
        tasks = board_data['columns']['In Progress']
        target = next((t for t in tasks if t['id'] == task_id), None)
        
        self.assertIsNotNone(target, "Task chưa qua cột In Progress")
        self.assertEqual(target['progress']['done'], 1)
        print(f"✅ [4] Board Data Verified")

        # [BƯỚC 5] LOGS
        res = self.client.get(f'/api/v1/tasks/{task_id}/activities', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertGreater(len(res.json), 0)
        print(f"✅ [5] Logs Verified")

if __name__ == '__main__':
    unittest.main()