import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock
from functools import wraps

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

class TestAnalyticsAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n=== SETUP: Khởi tạo Test Analytics ===")
        
        # 1. MOCK AUTH MIDDLEWARE
        cls.auth_patcher = patch('api.middleware.auth_required')
        cls.mock_auth = cls.auth_patcher.start()

        def mock_decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                from flask import g
                g.user_id = 1
                g.user_role = 'Lecturer' 
                return f(*args, **kwargs)
            return wrapper
        
        cls.mock_auth.side_effect = mock_decorator

        # 2. IMPORT APP SAU KHI ĐÃ PATCH
        from app import create_app
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        cls.auth_patcher.stop()

    @patch('infrastructure.services.analytics_service.AnalyticsService.get_student_dashboard')
    def test_01_student_dashboard(self, mock_service):
        """Test API Dashboard dành cho sinh viên"""
        print("\n--- TEST 1: Student Dashboard ---")
        
        # Giả lập dữ liệu trả về từ Service
        mock_service.return_value = {
            "upcoming_deadlines": [{"id": 1, "name": "Sprint 1", "deadline": "2026-02-15T00:00:00"}],
            "active_tasks": [{"id": 10, "title": "Làm Mockup", "status": "In Progress"}],
            "new_notifications": []
        }

        res = self.client.get('/api/v1/dashboard/student')
        
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(len(data['upcoming_deadlines']), 1)
        self.assertEqual(data['active_tasks'][0]['title'], "Làm Mockup")
        print("✅ Student Dashboard: OK")

    @patch('infrastructure.services.analytics_service.AnalyticsService.get_lecturer_dashboard')
    def test_02_lecturer_dashboard_success(self, mock_service):
        """Test API Dashboard dành cho giảng viên (Quyền hợp lệ)"""
        print("\n--- TEST 2: Lecturer Dashboard Success ---")
        
        mock_service.return_value = {
            "pending_grading_count": 5,
            "lagging_teams": [{"team_id": 1, "team_name": "Nhóm 1", "overdue_tasks": 3}]
        }

        res = self.client.get('/api/v1/dashboard/lecturer')
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['pending_grading_count'], 5)
        print("✅ Lecturer Dashboard: OK")

    def test_03_lecturer_dashboard_forbidden(self):
        """Test API Dashboard giảng viên bị từ chối nếu role là Student"""
        print("\n--- TEST 3: Lecturer Dashboard Forbidden ---")
        
        with self.app.app_context():
            with patch('api.controllers.analytics_controller.g') as mock_g:
                mock_g.user_role = 'Student'
                mock_g.user_id = 1
                
                # Thực hiện gọi API
                res = self.client.get('/api/v1/dashboard/lecturer')
                
                # Kiểm tra mã lỗi 403 Forbidden
                self.assertEqual(res.status_code, 403)
                
                data = res.get_json()
                self.assertEqual(data['error'], "Forbidden")
                
        print("✅ Permission Check: OK")

    @patch('infrastructure.services.analytics_service.AnalyticsService.get_clo_attainment')
    def test_04_clo_attainment(self, mock_service):
        """Test thống kê mức độ đạt chuẩn đầu ra"""
        print("\n--- TEST 4: CLO Attainment ---")
        
        mock_service.return_value = {
            "subject_id": 101,
            "average_score": 82.5
        }

        res = self.client.get('/api/v1/analytics/clo-attainment')
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['average_score'], 82.5)
        print("✅ CLO Attainment: OK")

if __name__ == '__main__':
    unittest.main()