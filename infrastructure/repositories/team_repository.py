from sqlalchemy.orm import Session
from infrastructure.models.team_model import TeamModel, TopicModel, TeamRequestModel, TeamMemberModel

class TeamRepository:
    def __init__(self, db: Session):
        self.db = db

    # --- TEAM CORE ---
    def get_by_id(self, team_id):
        return self.db.query(TeamModel).filter_by(id=team_id).first()

    # --- TOPIC MANAGEMENT ---
    def create_topic(self, topic: TopicModel):
        self.db.add(topic)
        self.db.commit()
        return topic

    def get_available_topics(self):
        """Lấy các đề tài ĐÃ DUYỆT và CÒN SLOT"""
        return self.db.query(TopicModel).filter(
            TopicModel.status == 'APPROVED',
            TopicModel.current_slots < TopicModel.max_slots
        ).all()

    def approve_topic(self, topic_id, status):
        topic = self.db.query(TopicModel).filter_by(id=topic_id).first()
        if topic:
            topic.status = status
            self.db.commit()
            return topic
        return None

    def register_topic_safe(self, team_id: int, topic_id: int):
        """
        [ALGORITHM]: Concurrency Control
        Sử dụng UPDATE ... WHERE ... để đảm bảo tính nguyên tử (Atomicity).
        Nếu 2 request cùng chạy 1 lúc, chỉ 1 cái update thành công row count > 0.
        """
        # 1. Thử xí chỗ (Increment slot nếu chưa full)
        updated_rows = self.db.query(TopicModel).filter(
            TopicModel.id == topic_id,
            TopicModel.status == 'APPROVED',
            TopicModel.current_slots < TopicModel.max_slots
        ).update(
            {TopicModel.current_slots: TopicModel.current_slots + 1},
            synchronize_session=False
        )

        if updated_rows == 0:
            return False, "Đề tài đã đầy hoặc không tồn tại."

        # 2. Gán topic cho team
        team = self.get_by_id(team_id)
        team.project_id = topic_id
        
        self.db.commit()
        return True, "Đăng ký thành công"

    # --- MEMBER REQUESTS ---
    def create_request(self, request: TeamRequestModel):
        self.db.add(request)
        self.db.commit()
        return request
    def create_team_with_leader(self, name, class_id, leader_id):
        """
        Transaction: Tạo Team + Thêm Leader vào TeamMember
        """
        try:
            # Bước 1: Tạo Team
            new_team = TeamModel(
                name=name,
                class_id=class_id,
                leader_id=leader_id
            )
            self.db.add(new_team)
            self.db.flush() 

            # Bước 2: Thêm Leader
            leader_member = TeamMemberModel(
                team_id=new_team.id,
                user_id=leader_id,
                role='Leader'
            )
            self.db.add(leader_member)

            # Bước 3: Chốt sổ
            self.db.commit()
            self.db.refresh(new_team)
            return new_team
        except Exception as e:
            self.db.rollback()
            raise e

    def get_request(self, req_id):
        return self.db.query(TeamRequestModel).filter_by(id=req_id).first()

    def approve_join_request_transaction(self, request_id):
        """
        Transaction: Đổi trạng thái Request -> Thêm vào TeamMember
        """
        try:
            req = self.get_request(request_id)
            if not req or req.status != 'PENDING':
                return False

            # 1. Update Request
            req.status = 'APPROVED'
            
            # 2. Add Member
            new_member = TeamMemberModel(team_id=req.team_id, user_id=req.user_id, role='Member')
            self.db.add(new_member)
            
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False

    def remove_member(self, team_id, user_id):
        """Xóa thành viên khỏi nhóm"""
        member = self.db.query(TeamMemberModel).filter_by(team_id=team_id, user_id=user_id).first()
        if member:
            self.db.delete(member)
            self.db.commit()
            return True
        return False