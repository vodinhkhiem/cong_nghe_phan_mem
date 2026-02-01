import unittest
import sys
import os
import json
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from app import create_app
from infrastructure.databases.mssql import SessionLocal
from infrastructure.models.user_model import UserModel
from infrastructure.models.team_model import TeamModel, TeamMemberModel, TopicModel
from infrastructure.models.project_model import ProjectModel, ProjectMilestoneModel
from infrastructure.models.academic_model import SubjectModel, ClassModel, SyllabusModel

class TestEvaluationFlow(unittest.TestCase):
    shared_submission_id = None
    shared_checkpoint_id = None

    @classmethod
    def setUpClass(cls):
        print("\n=== SETUP: Khởi tạo Test Evaluation ===")
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()
        cls.session = SessionLocal()
        
        # --- 1. TẠO DATA & LƯU ID  ---
        
        # Users
        lec = cls.create_test_user("teacher_eval@test.com", "Lecturer")
        cls.lecturer_id = lec.id
        
        st1 = cls.create_test_user("st1_eval@test.com", "Student")
        cls.student1_id = st1.id
        
        st2 = cls.create_test_user("st2_eval@test.com", "Student")
        cls.student2_id = st2.id

        # Academic
        subject = cls.get_or_create(SubjectModel, code="TEST_SUB", name="Test Subject")
        syllabus = cls.get_or_create(SyllabusModel, subject_id=subject.id, content="Test Content")
        clazz = cls.get_or_create(ClassModel, name="TEST_CLASS", subject_id=subject.id, lecturer_id=cls.lecturer_id)
        
        # Topic & Project
        topic = cls.get_or_create(TopicModel, name="Test Topic Eval", description="Desc", lecturer_id=cls.lecturer_id, status="APPROVED")
        project = cls.get_or_create(ProjectModel, title="Test Project Eval", status="Approved", syllabus_id=syllabus.id, created_by=cls.lecturer_id)
        
        # Milestone
        milestone = cls.get_or_create(ProjectMilestoneModel, 
                                      name="Sprint 1 Test", 
                                      project_id=project.id,
                                      deadline=datetime.now() + timedelta(days=5))
        cls.milestone_id = milestone.id  # <--- CHỈ LƯU ID

        # Team
        team = cls.get_or_create(TeamModel, name="Test Team Eval", class_id=clazz.id, project_id=topic.id, leader_id=cls.student1_id)
        cls.team_id = team.id            # <--- CHỈ LƯU ID

        # Add Members
        cls.add_to_team(cls.team_id, cls.student1_id, "Leader")
        cls.add_to_team(cls.team_id, cls.student2_id, "Member")

        # --- 2. LẤY TOKEN ---
        cls.token_st1 = cls.login_user("st1_eval@test.com")
        cls.token_st2 = cls.login_user("st2_eval@test.com")
        cls.token_lec = cls.login_user("teacher_eval@test.com")

        print("✅ Setup Data & Auth Tokens Complete!")

    @classmethod
    def tearDownClass(cls):
        cls.session.close()

    # --- HELPER ---
    @classmethod
    def get_or_create(cls, model, **kwargs):
        instance = cls.session.query(model).filter_by(**kwargs).first()
        if not instance:
            instance = model(**kwargs)
            cls.session.add(instance)
            cls.session.commit()
            cls.session.refresh(instance) # Refresh để lấy ID
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
    def add_to_team(cls, team_id, user_id, role):
        member = cls.session.query(TeamMemberModel).filter_by(team_id=team_id, user_id=user_id).first()
        if not member:
            member = TeamMemberModel(team_id=team_id, user_id=user_id, role=role)
            cls.session.add(member)
            cls.session.commit()

    @classmethod
    def login_user(cls, email):
        res = cls.client.post('/api/v1/auth/login', json={"email": email, "password": "123"})
        return res.json['accessToken']

    # --- TESTS ---

    def test_01_get_milestones(self):
        print("\n--- TEST 1: Get Milestones ---")
        headers = {'Authorization': f'Bearer {self.token_st1}'}
        res = self.client.get('/api/v1/evaluation/milestones', headers=headers)
        
        # Debug lỗi 500
        if res.status_code != 200:
            print(f"❌ Error Body: {res.get_data(as_text=True)}")

        self.assertEqual(res.status_code, 200)
        data = res.json
        found = any(m['id'] == self.milestone_id for m in data)
        self.assertTrue(found, "Không tìm thấy Milestone vừa tạo!")

    def test_02_submit_assignment(self):
        print("\n--- TEST 2: Submit Assignment ---")
        headers = {'Authorization': f'Bearer {self.token_st1}'}
        
        payload = {
            "team_id": self.team_id,
            "milestone_id": self.milestone_id,
            "file_url": "https://github.com/test/repo_v1"
        }

        res = self.client.post('/api/v1/evaluation/submissions', headers=headers, json=payload)
        
        if res.status_code != 201:
            print(f"❌ Error Body: {res.get_data(as_text=True)}")

        self.assertEqual(res.status_code, 201)
        
        TestEvaluationFlow.shared_submission_id = res.json['submission_id']
        TestEvaluationFlow.shared_checkpoint_id = res.json.get('checkpoint_id') 
        print(f"   [OK] Checkpoint ID: {TestEvaluationFlow.shared_checkpoint_id}")

    def test_03_peer_review(self):
        print("\n--- TEST 3: Peer Review ---")
        headers = {'Authorization': f'Bearer {self.token_st1}'}
        
        if not TestEvaluationFlow.shared_checkpoint_id:
             self.skipTest("No checkpoint to review")

        payload = {
            "target_id": self.student2_id,
            "checkpoint_id": TestEvaluationFlow.shared_checkpoint_id,
            "score": 9,
            "comment": "Good job"
        }
        
        res = self.client.post('/api/v1/evaluation/peer-reviews', headers=headers, json=payload)
        self.assertEqual(res.status_code, 201)

    def test_04_grading_and_transcript(self):
        print("\n--- TEST 4: Grading & Transcript ---")
        
        if not TestEvaluationFlow.shared_submission_id:
            self.skipTest("Skipping because submission failed in Test 2")

        headers_lec = {'Authorization': f'Bearer {self.token_lec}'}
        payload = {
            "submission_id": TestEvaluationFlow.shared_submission_id,
            "score": 8.5,
            "feedback": "Good"
        }
        res = self.client.post('/api/v1/evaluation/grades', headers=headers_lec, json=payload)
        self.assertEqual(res.status_code, 200)

if __name__ == '__main__':
    unittest.main()