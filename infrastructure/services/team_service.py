from infrastructure.repositories.team_repository import TeamRepository
from infrastructure.models.team_model import TopicModel, TeamRequestModel

class TeamService:
    def __init__(self, db):
        self.repo = TeamRepository(db)

    # --- TOPIC SERVICES ---
    def propose_topic(self, data, lecturer_id):
        new_topic = TopicModel(
            name=data['name'],
            description=data.get('description'),
            lecturer_id=lecturer_id,
            status='PENDING', # Mặc định chờ duyệt
            max_slots=data.get('max_slots', 3)
        )
        return self.repo.create_topic(new_topic)

    def approve_topic(self, topic_id, status):
        # Chỉ trưởng bộ môn mới được gọi (Check ở Controller)
        if status not in ['APPROVED', 'REJECTED']:
            raise ValueError("Status không hợp lệ")
        return self.repo.approve_topic(topic_id, status)

    def get_available_topics(self):
        return self.repo.get_available_topics()

    def register_topic(self, team_id, topic_id, user_id):
        # 1. Check quyền Leader
        team = self.repo.get_by_id(team_id)
        if not team or team.leader_id != user_id:
            raise PermissionError("Chỉ Leader mới được đăng ký đề tài")
            
        # 2. Gọi hàm Safe Registration ở Repo
        success, msg = self.repo.register_topic_safe(team_id, topic_id)
        if not success:
            raise ValueError(msg)
        return True

    # --- MEMBERSHIP SERVICES ---
    # Bổ sung vào class TeamService trong team_service.py
    def create_team(self, data, leader_id):
        """Tạo nhóm mới và tự động gán người tạo làm Leader"""
        name = data.get('name')
        class_id = data.get('class_id')
        
        if not name or not class_id:
            raise ValueError("Thiếu tên nhóm hoặc mã lớp")
            
        # Gọi sang repository để thực hiện transaction (Tạo Team + Add Member)
        team = self.repo.create_team_with_leader(name, class_id, leader_id)
        return team
    def request_join_team(self, team_id, user_id):
        # TODO: Check xem user này đã có nhóm nào chưa (Business Rule)
        
        req = TeamRequestModel(
            team_id=team_id,
            user_id=user_id,
            type='JOIN',
            status='PENDING'
        )
        return self.repo.create_request(req)

    def process_join_request(self, req_id, action, user_id):
        """Action: 'approve' | 'reject'"""
        req = self.repo.get_request(req_id)
        if not req: 
            raise ValueError("Request not found")

        # Check quyền Leader của team đó
        team = self.repo.get_by_id(req.team_id)
        if team.leader_id != user_id:
            raise PermissionError("Chỉ Leader mới được duyệt thành viên")

        if action == 'approve':
            return self.repo.approve_join_request_transaction(req_id)
        elif action == 'reject':
            req.status = 'REJECTED'
            self.repo.db.commit()
            return True
        return False

    def leave_team(self, team_id, user_id):
        team = self.repo.get_by_id(team_id)
        if team.leader_id == user_id:
            raise ValueError("Leader không được rời nhóm (Hãy chuyển quyền trước)")
            
        return self.repo.remove_member(team_id, user_id)