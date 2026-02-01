from sqlalchemy.exc import SQLAlchemyError
from infrastructure.databases.mssql import session
from infrastructure.models.team_model import TeamModel
from infrastructure.models.team_member_model import TeamMemberModel
from infrastructure.models.topic_model import TopicModel
from infrastructure.models.team_request_model import TeamRequestModel

class TeamRepository:
    # PHẦN 1: QUẢN LÝ TEAM CORE
    def create_team_with_transaction(self, name, class_id, leader_id):
        """
        Tạo nhóm và set Leader.
        [ALGORITHM]: ACID Transaction (Atomicity)
        Mục đích: Đảm bảo tính toàn vẹn, cả 2 lệnh Insert phải cùng thành công hoặc cùng thất bại.
        """
        try:
            # 1. Insert Team
            new_team = TeamModel(name=name, class_id=class_id, leader_id=leader_id)
            session.add(new_team)
            session.flush() # Lấy ID ngay lập tức

            # 2. Insert Member (Leader)
            new_member = TeamMemberModel(team_id=new_team.id, user_id=leader_id, role='Leader')
            session.add(new_member)
            
            session.commit()
            return new_team
        except SQLAlchemyError as e:
            session.rollback() # Hoàn tác nếu lỗi
            raise e

    def get_team_by_id(self, team_id):
        return session.query(TeamModel).filter_by(id=team_id).first()

    def get_team_member(self, team_id, user_id):
        # [QUERY]: Tìm thành viên cụ thể trong nhóm
        return session.query(TeamMemberModel).filter_by(team_id=team_id, user_id=user_id).first()

    def remove_member(self, team_id, user_id):
        """Xóa thành viên khỏi nhóm"""
        try:
            member = self.get_team_member(team_id, user_id)
            if member:
                session.delete(member)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            raise e

    # PHẦN 2: QUẢN LÝ ĐỀ TÀI (TOPIC)
    def create_topic(self, title, description, created_by, is_gv, status):
        try:
            topic = TopicModel(
                title=title, 
                description=description, 
                created_by=created_by, 
                is_suggested_by_gv=is_gv, 
                status=status
            )
            session.add(topic)
            session.commit()
            return topic
        except SQLAlchemyError as e:
            session.rollback()
            raise e

    def get_all_topics(self):
        # [QUERY]: Lấy toàn bộ danh sách đề tài
        return session.query(TopicModel).all()

    def get_topic_by_id(self, topic_id):
        return session.query(TopicModel).filter_by(id=topic_id).first()

    def update_topic(self, topic):
        """Lưu các thay đổi của object topic xuống DB"""
        try:
            session.commit()
            return topic
        except SQLAlchemyError as e:
            session.rollback()
            raise e
            
    def assign_topic_to_team(self, team_id, project_id):
        """Gán đề tài cho nhóm (Logic cũ)"""
        try:
            team = self.get_team_by_id(team_id)
            if team:
                team.project_id = project_id
                session.commit()
                return team
            return None
        except SQLAlchemyError as e:
            session.rollback()
            raise e

    # PHẦN 3: QUẢN LÝ YÊU CẦU/LỜI MỜI (REQUESTS)
    def create_request(self, team_id, user_id, type):
        try:
            # [LOGIC]: Kiểm tra trùng lặp (Idempotency check)
            existing = session.query(TeamRequestModel).filter_by(
                team_id=team_id, user_id=user_id, status='Pending', type=type
            ).first()
            if existing: return existing

            req = TeamRequestModel(team_id=team_id, user_id=user_id, type=type, status='Pending')
            session.add(req)
            session.commit()
            return req
        except SQLAlchemyError as e:
            session.rollback()
            raise e

    def get_request_by_id(self, request_id):
        return session.query(TeamRequestModel).filter_by(id=request_id).first()

    def resolve_request_transaction(self, request, is_approved):
        """
        [ALGORITHM]: Transactional State Transition
        Xử lý yêu cầu: Cập nhật trạng thái Request -> (Nếu Approve) Thêm Member
        """
        try:
            # 1. Cập nhật trạng thái Request
            request.status = 'Approved' if is_approved else 'Rejected'
            
            # 2. Nếu Approved -> Thêm vào bảng Member
            if is_approved:
                # Kiểm tra lại lần nữa xem đã vào nhóm chưa
                exists = self.get_team_member(request.team_id, request.user_id)
                if not exists:
                    new_member = TeamMemberModel(
                        team_id=request.team_id, 
                        user_id=request.user_id, 
                        role='Member'
                    )
                    session.add(new_member)
            
            session.commit()
            return request
        except SQLAlchemyError as e:
            session.rollback()
            raise e