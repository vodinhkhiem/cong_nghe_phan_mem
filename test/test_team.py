import unittest
import json
import sys
import os
from datetime import datetime
from unittest.mock import patch
from functools import wraps

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from app import create_app
from infrastructure.databases.mssql import SessionLocal, engine
from sqlalchemy.orm import Session

# Import Models
from infrastructure.models.user_model import UserModel
from infrastructure.models.academic_model import ClassModel, SubjectModel
from infrastructure.models.team_model import TeamModel, TeamMemberModel, TopicModel, TeamRequestModel, WorkspaceModel

class TestTeamIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n=== SETUP: Bắt đầu Mock Auth & Khởi tạo Test Team ===")
        
        # 1. BẮT ĐẦU MOCK MIDDLEWARE NGAY LẬP TỨC ĐỂ TRÁNH LỖI 401
        cls.auth_patcher = patch('api.middleware.auth_required')
        cls.mock_auth = cls.auth_patcher.start()

        def mock_decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                from flask import g, request
                uid = request.headers.get('X-User-ID', '1')
                g.user_id = int(uid)
                g.user_role = 'Lecturer' 
                return f(*args, **kwargs)
            return wrapper
        
        cls.mock_auth.side_effect = mock_decorator

        # 2. KHỞI TẠO APP SAU KHI ĐÃ PATCH
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()
        cls.session = SessionLocal()

        # 3. SETUP DỮ LIỆU CỐ ĐỊNH (User, Class, Subject)
        cls.setup_base_data()
        print("✅ Auth đã được Mock & Dữ liệu base đã sẵn sàng.")

    @classmethod
    def tearDownClass(cls):
        cls.session.close()
        cls.auth_patcher.stop()

    @classmethod
    def setup_base_data(cls):
        leader = cls.get_or_create(UserModel, email="leader_team@test.com", 
                                  full_name="Team Leader", password="123", role="Student", status=True)
        cls.leader_id = leader.id

        # Member
        member = cls.get_or_create(UserModel, email="member_team@test.com", 
                                  full_name="Team Member", password="123", role="Student", status=True)
        cls.member_id = member.id

        # Subject & Class
        subject = cls.get_or_create(SubjectModel, code="SUB_TEAM", name="Teamwork Subject")
        clazz = cls.get_or_create(ClassModel, name="CLASS_TEAM_01", 
                                 subject_id=subject.id, semester="FA24", lecturer_id=leader.id)
        cls.class_id = clazz.id

    @classmethod
    def get_or_create(cls, model, **kwargs):
        instance = cls.session.query(model).filter_by(**{k: v for k, v in kwargs.items() if k in ['email', 'code', 'name']}).first()
        if not instance:
            instance = model(**kwargs)
            cls.session.add(instance)
            cls.session.commit()
            cls.session.refresh(instance)
        return instance

    def get_db_session(self):
        return SessionLocal()

    # TEST CASE 1: CREATE TEAM
    def test_01_create_team_flow(self):
        print("\n[Test 1] 👥 Testing Create Team Flow...")
        payload = {
            "name": "Super Dragon Team",
            "class_id": self.class_id
        }
        
        res = self.client.post('/api/v1/teams', 
                               json=payload, 
                               headers={'X-User-ID': str(self.leader_id)})
        
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        print(f"   ✅ API tạo nhóm thành công. Team ID: {data['id']}")

    # TEST CASE 2: TOPIC LIFECYCLE
    def test_02_topic_lifecycle(self):
        print("\n[Test 2] 📝 Testing Topic Lifecycle...")
        
        # BƯỚC 1: GV Đề xuất đề tài
        payload_topic = {
            "name": "Xây dựng hệ thống IoT " + str(datetime.now().timestamp()),
            "description": "Dùng Arduino và Python",
            "max_slots": 2
        }
        res_propose = self.client.post('/api/v1/topics/propose', 
                                       json=payload_topic, 
                                       headers={'X-User-ID': str(self.leader_id)})
        self.assertEqual(res_propose.status_code, 201)
        topic_id = res_propose.get_json()['id']

        # BƯỚC 2: Duyệt đề tài
        self.client.put(f'/api/v1/topics/{topic_id}/approval', 
                        json={"status": "APPROVED"}, 
                        headers={'X-User-ID': str(self.leader_id)})

        # BƯỚC 3: Tạo nhóm & Đăng ký
        team = self.get_or_create(TeamModel, name="Topic Tester Team", class_id=self.class_id, leader_id=self.leader_id)
        
        payload_reg = {"topic_id": topic_id}
        res_reg = self.client.post(f'/api/v1/teams/{team.id}/register-topic', 
                                    json=payload_reg, 
                                    headers={'X-User-ID': str(self.leader_id)})
    
        self.assertEqual(res_reg.status_code, 200)
        print("   ✅ Nhóm đăng ký đề tài thành công.")

    # TEST CASE 3: JOIN REQUEST
    def test_03_join_request_flow(self):
        print("\n[Test 3] 🤝 Testing Join Request Flow...")
        team = self.get_or_create(TeamModel, name="Join Request Team", class_id=self.class_id, leader_id=self.leader_id)

        # 1. Member xin vào nhóm
        res_req = self.client.post(f'/api/v1/teams/{team.id}/join-request', 
                                    headers={'X-User-ID': str(self.member_id)})
        self.assertEqual(res_req.status_code, 201)

        # 2. Lấy Request ID từ DB để duyệt
        session = self.get_db_session()
        request_obj = session.query(TeamRequestModel).filter_by(team_id=team.id, status='PENDING').first()
        
        # 3. Leader Duyệt
        res_approve = self.client.put(f'/api/v1/teams/requests/{request_obj.id}/approve', 
                                       headers={'X-User-ID': str(self.leader_id)})
        self.assertEqual(res_approve.status_code, 200)
        print("   ✅ Thành viên đã tham gia nhóm thành công.")
        session.close()

if __name__ == '__main__':
    unittest.main()