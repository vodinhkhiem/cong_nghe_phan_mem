import unittest
import sys
import os
from unittest.mock import MagicMock

# FIX IMPORT PATH
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_path = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_path)

# IMPORT SERVICE
try:
    from services.team_service import TeamService
    from services.kanban_service import KanbanService
except ImportError as e:
    print(f"❌ Lỗi Import: {e}. Hãy đảm bảo bạn đang đứng ở thư mục gốc dự án.")
    sys.exit(1)

# GIẢ LẬP MODELS (MOCKING)
class FakeTeam:
    def __init__(self, id, leader_id, project_id=None):
        self.id = id
        self.leader_id = leader_id
        self.project_id = project_id

class FakeTopic:
    def __init__(self, id, status):
        self.id = id
        self.status = status

class FakeRequest:
    def __init__(self, id, team_id, user_id, type, status='Pending'):
        self.id = id
        self.team_id = team_id
        self.user_id = user_id
        self.type = type # 'JOIN' hoặc 'INVITE'
        self.status = status

# BỘ TEST CASE
class TestIntegratedFeatures(unittest.TestCase):
    
    def setUp(self):
        # Mock Repository
        self.mock_repo = MagicMock()
        # Inject vào Service
        self.service = TeamService()
        self.service.team_repo = self.mock_repo

    # 1. TEST LUỒNG ĐỀ TÀI (TOPIC)
    def test_topic_creation_status(self):
        """Test: SV tạo -> Pending, GV tạo -> Approved"""
        
        # Case 1: Student
        self.service.create_topic({'title': 'A'}, user_id=1, user_role='Student')
        # Kiểm tra tham số gọi xuống repo
        self.mock_repo.create_topic.assert_called_with(
            title='A', description=None, created_by=1, is_gv=False, status='Pending'
        )
        
        # Case 2: Lecturer
        self.service.create_topic({'title': 'B'}, user_id=2, user_role='Lecturer')
        self.mock_repo.create_topic.assert_called_with(
            title='B', description=None, created_by=2, is_gv=True, status='Approved'
        )
        print("✅ [Topic] Creation Status Logic: PASS")

    def test_approve_topic_permission(self):
        """Test: SV không được duyệt đề tài"""
        with self.assertRaises(PermissionError):
            self.service.approve_topic(topic_id=1, user_role='Student')
        print("✅ [Topic] Approval Permission: PASS")

    def test_register_topic_validation(self):
        """Test: Không được đăng ký đề tài chưa duyệt"""
        # Giả lập đề tài ID 10 đang Pending
        self.mock_repo.get_topic_by_id.return_value = FakeTopic(id=10, status='Pending')
        self.mock_repo.get_team_by_id.return_value = FakeTeam(id=1, leader_id=99)
        
        # Leader (ID 99) cố tình đăng ký
        with self.assertRaises(ValueError) as ctx:
            self.service.register_topic_for_team(team_id=1, data={'project_id': 10}, user_id=99)
        
        self.assertIn("chưa được duyệt", str(ctx.exception))
        print("✅ [Topic] Register Validation: PASS")

    # 2. TEST LUỒNG THÀNH VIÊN (MEMBERSHIP)
    def test_join_request_flow(self):
        """Test: Leader duyệt đơn xin vào"""
        # Giả lập Request xin vào (JOIN)
        req = FakeRequest(id=100, team_id=1, user_id=5, type='JOIN')
        self.mock_repo.get_request_by_id.return_value = req
        # Giả lập Team có Leader là ID 99
        self.mock_repo.get_team_by_id.return_value = FakeTeam(id=1, leader_id=99)
        
        # Leader (99) duyệt -> Thành công
        self.service.respond_to_request(request_id=100, action='approve', user_id=99)
        self.mock_repo.resolve_request_transaction.assert_called()
        print("✅ [Member] Join Request Approval: PASS")

    def test_invite_response_flow(self):
        """Test: Người được mời đồng ý tham gia"""
        # Giả lập Request mời (INVITE) cho User ID 10
        req = FakeRequest(id=200, team_id=1, user_id=10, type='INVITE')
        self.mock_repo.get_request_by_id.return_value = req
        self.mock_repo.get_team_by_id.return_value = FakeTeam(id=1, leader_id=99)
        
        # User 10 đồng ý -> Thành công
        self.service.respond_to_request(request_id=200, action='approve', user_id=10)
        self.mock_repo.resolve_request_transaction.assert_called()
        print("✅ [Member] Invite Response: PASS")

    def test_invite_response_wrong_user(self):
        """Test: Người khác (không phải người được mời) cố tình đồng ý -> Lỗi"""
        req = FakeRequest(id=200, team_id=1, user_id=10, type='INVITE')
        self.mock_repo.get_request_by_id.return_value = req
        self.mock_repo.get_team_by_id.return_value = FakeTeam(id=1, leader_id=99)
        
        # User 5 (người lạ) cố tình đồng ý thay cho User 10
        with self.assertRaises(PermissionError):
            self.service.respond_to_request(request_id=200, action='approve', user_id=5)
        print("✅ [Member] Invite Security Check: PASS")

if __name__ == '__main__':
    unittest.main()