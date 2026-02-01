import unittest
import sys
import os
import json
from unittest.mock import patch

# Cấu hình đường dẫn
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from app import create_app
from infrastructure.databases.mssql import SessionLocal
from infrastructure.models.user_model import UserModel
from infrastructure.models.task_model import TaskModel
from infrastructure.models.team_model import WorkspaceModel, TeamModel, TopicModel
from infrastructure.models.academic_model import SubjectModel, ClassModel

class TestAIFeatures(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Khởi tạo dữ liệu mẫu: User, Team, Task"""
        print("\n=== SETUP: Khởi tạo Test AI ===")
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()
        cls.session = SessionLocal()

        # 1. Tạo User
        user = cls.create_test_user("student_ai@test.com", "Student")
        cls.user_id = user.id

        lecturer = cls.create_test_user("teacher_ai@test.com", "Lecturer")
        cls.lecturer_id = lecturer.id
        print(f"   [DEBUG] Lecturer ID: {cls.lecturer_id}")

        subject = cls.get_or_create(SubjectModel, code="AI_SUB_TEST", name="AI Subject")

        clazz = cls.get_or_create(ClassModel, 
                                  name="AI_CLASS_TEST", 
                                  subject_id=subject.id, 
                                  lecturer_id=cls.lecturer_id)

        topic = cls.get_or_create(TopicModel, 
                                  name="AI Research Topic", 
                                  description="AI Desc", 
                                  lecturer_id=cls.lecturer_id, 
                                  status="APPROVED")

        # 2. Tạo Team & Workspace 
        team = cls.get_or_create(TeamModel, 
                                 name="AI Test Team",
                                 class_id=clazz.id,  
                                 project_id=topic.id, 
                                 leader_id=cls.user_id)
        ws = cls.get_or_create(WorkspaceModel, team_id=team.id)
        
        # 3. Tạo Task mẫu 
        task = cls.get_or_create(TaskModel, 
                                 title="Xay dung chuc nang dang nhap", 
                                 description="Lam ca Frontend va Backend",
                                 workspace_id=ws.id,
                                 assignee_id=cls.user_id,
                                 status="TODO")
        cls.task_id = task.id # Chỉ lưu ID

        cls.session.commit()

        # 4. Login lấy Token
        cls.token = cls.login_user("student_ai@test.com")

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
    @patch('infrastructure.services.ai_llm_client.AILLMClient.generate_response')
    def test_01_chat_general(self, mock_generate):
        """Test 1: Chat thông thường (Mock AI trả lời)"""
        print("\n--- TEST 1: Chat General ---")
        
        # Giả lập AI trả lời
        mock_generate.return_value = "Xin chào, tôi là AI hỗ trợ học tập."

        headers = {'Authorization': f'Bearer {self.token}'}
        payload = {"message": "Hello AI"}

        res = self.client.post('/api/v1/ai/chat', headers=headers, json=payload)
        
        self.assertEqual(res.status_code, 200)
        data = res.json
        print(f"   AI Response: {data['response']}")
        
        self.assertEqual(data['response'], "Xin chào, tôi là AI hỗ trợ học tập.")
        self.assertIn("conversation_id", data)

    @patch('infrastructure.services.ai_llm_client.AILLMClient.generate_response')
    def test_02_breakdown_task(self, mock_generate):
        """Test 2: Chia nhỏ Task (Test logic parse JSON)"""
        print("\n--- TEST 2: Breakdown Task ---")
        
        mock_response = """
        Dưới đây là các bước:
        ```json
        ["Thiết kế UI Login", "Viết API /auth/login", "Testing"]
        ```
        """
        mock_generate.return_value = mock_response

        headers = {'Authorization': f'Bearer {self.token}'}
        
        # Gọi API
        res = self.client.post(f'/api/v1/ai/tasks/{self.task_id}/breakdown', headers=headers, json={})
        
        if res.status_code != 200:
            print(f"❌ Error: {res.get_data(as_text=True)}")

        self.assertEqual(res.status_code, 200)
        data = res.json
        print(f"   Suggestion: {data['suggestion']}")
        
        self.assertIsInstance(data['suggestion'], list)
        self.assertEqual(len(data['suggestion']), 3)
        self.assertEqual(data['suggestion'][0], "Thiết kế UI Login")

    @patch('infrastructure.services.ai_llm_client.AILLMClient.generate_response')
    def test_03_explain_code(self, mock_generate):
        """Test 3: Giải thích code"""
        print("\n--- TEST 3: Explain Code ---")
        
        mock_generate.return_value = "Lỗi này do thiếu dấu hai chấm."
        
        headers = {'Authorization': f'Bearer {self.token}'}
        payload = {
            "code_snippet": "if x > 5 print('hello')",
            "error_log": "SyntaxError: invalid syntax"
        }

        res = self.client.post('/api/v1/ai/code/explain', headers=headers, json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['explanation'], "Lỗi này do thiếu dấu hai chấm.")

    def test_04_get_history(self):
        """Test 4: Xem lịch sử chat (Verify DB persistence)"""
        print("\n--- TEST 4: Get Chat History ---")
        headers = {'Authorization': f'Bearer {self.token}'}
        
        res = self.client.get('/api/v1/ai/history', headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json
        
        print(f"   Found {len(data)} messages.")
        self.assertGreaterEqual(len(data), 2)
        
        last_msg = data[0] 
        print(f"   Latest msg: [{last_msg['sender']}] {last_msg['message']}")
    
    @patch('infrastructure.services.ai_llm_client.AILLMClient.generate_response')
    def test_05_ai_error_handling(self, mock_generate):
        """Test 5: Xử lý khi AI Client trả về lỗi kết nối"""
        print("\n--- TEST 5: AI Error Handling (Chat) ---")
        mock_generate.return_value = "Lỗi kết nối API Gemini"
        
        headers = {'Authorization': f'Bearer {self.token}'}
        res = self.client.post('/api/v1/ai/chat', headers=headers, json={"message": "fail test"})
       
        self.assertEqual(res.status_code, 200)
        self.assertIn("Lỗi", res.json['response'])
        print("   [OK] System handled API Error gracefully.")
    @patch('infrastructure.services.ai_llm_client.AILLMClient.generate_response')
    def test_06_breakdown_task_malformed_json(self, mock_generate):
        """Test 6: AI trả về text rác thay vì JSON Array"""
        print("\n--- TEST 6: Breakdown Task (Malformed JSON) ---")
        
        mock_generate.return_value = "Xin lỗi tôi không thể chia nhỏ task này."
        
        headers = {'Authorization': f'Bearer {self.token}'}
        res = self.client.post(f'/api/v1/ai/tasks/{self.task_id}/breakdown', headers=headers, json={})
        
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertIsInstance(data['suggestion'], list)
        self.assertEqual(data['suggestion'][0], "Xin lỗi tôi không thể chia nhỏ task này.")
        print("   [OK] Fallback mechanism worked for bad JSON.")

if __name__ == '__main__':
    unittest.main()