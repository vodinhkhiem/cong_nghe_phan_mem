import unittest
import json
from app import create_app
from unittest.mock import patch

class TestLMSAssistantAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.testing = True

    # --- 1. TEST ANALYTICS (Đúng cấu trúc Aggregation) ---
    
    def test_student_dashboard_structure(self):
        """Kiểm tra Dashboard SV có đủ 3 thành phần như Hình 1"""
        response = self.client.get('/dashboard/student')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        keys = data['data'].keys()
        self.assertTrue(all(k in keys for k in ['deadlines_sap_toi', 'tasks_dang_lam', 'thong_bao_moi']))

    def test_lecturer_dashboard_structure(self):
        """Kiểm tra Dashboard Giảng viên (Số bài cần chấm & Nhóm chậm tiến độ)"""
        response = self.client.get('/dashboard/lecturer')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('thong_ke_can_cham', data['data'])
        self.assertIn('nhom_cham_tien_do', data['data'])

    def test_clo_attainment(self):
        """Kiểm tra API thống kê CLO của Trưởng bộ môn"""
        response = self.client.get('/analytics/clo-attainment')
        self.assertEqual(response.status_code, 200)
        self.assertIn('thong_ke_clo', json.loads(response.data)['data'])

    # --- 2. TEST AI (Giả lập gọi AI và xử lý logic) ---

    @patch('ai_post.ask_gemini')
    def test_ai_chat_flow(self, mock_ai):
        mock_ai.return_value = "Phản hồi giả lập từ AI"
        payload = {"message": "Học Flask như thế nào?", "conversation_id": "123"}
        response = self.client.post('/ai/chat', 
                                    data=json.dumps(payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['reply'], "Phản hồi giả lập từ AI")

    @patch('ai_post.ask_gemini')
    def test_ai_task_breakdown(self, mock_ai):
        """Kiểm tra API chia nhỏ Task (Sử dụng ID động trên URL)"""
        mock_ai.return_value = "1. Làm UI\n2. Làm API"
        payload = {"task_description": "Làm web bán hàng"}
        # Test route với ID động <taskId>
        response = self.client.post('/ai/tasks/task_55/breakdown', 
                                    data=json.dumps(payload),
                                    content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['taskId'], 'task_55')

    @patch('ai_post.ask_gemini')
    def test_ai_code_explain_logic(self, mock_ai):
        mock_ai.return_value = "Giải thích lỗi: Thiếu dấu ngoặc"
        payload = {"code_snippet": "print('hi'", "error_log": "SyntaxError"}
        response = self.client.post('/ai/code/explain', 
                                    data=json.dumps(payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("explanation", json.loads(response.data))

    # --- 3. TEST ERROR HANDLING ---

    def test_ai_post_without_message(self):
        """Gửi JSON trống hoặc thiếu 'message' phải trả về 400"""
        response = self.client.post('/ai/chat', 
                                    data=json.dumps({}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()