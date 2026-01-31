from sqlalchemy.exc import SQLAlchemyError
from infrastructure.databases.mssql import session
from infrastructure.models.team_model import TeamModel
from infrastructure.models.team_member_model import TeamMemberModel

class TeamRepository:
    def create_team_with_transaction(self, name, class_id, leader_id):
        """
        Tạo nhóm mới và gán người tạo làm Leader ngay lập tức.
        """
        # [ALGORITHM]: ACID Transaction (Atomicity)
        # Mục đích: Đảm bảo cả 2 hành động (Tạo Team + Thêm Leader) phải cùng thành công hoặc cùng thất bại.
        try:
            # Bước 1: Insert dữ liệu vào bảng Team
            new_team = TeamModel(name=name, class_id=class_id, leader_id=leader_id)
            session.add(new_team)
            session.flush() 

            # Bước 2: Insert dữ liệu vào bảng TeamMember
            new_member = TeamMemberModel(
                team_id=new_team.id,
                user_id=leader_id,
                role='Leader'
            )
            session.add(new_member)
            
            # [CHECKPOINT]: Nếu không có lỗi gì xảy ra, lưu vào DB
            session.commit()
            return new_team
        except SQLAlchemyError as e:
            # [ROLLBACK]: Nếu có lỗi bất kỳ, hoàn tác mọi thay đổi để tránh rác dữ liệu
            session.rollback()
            raise e

    def get_team_by_id(self, team_id):
        # Truy vấn đơn giản lấy thông tin nhóm
        return session.query(TeamModel).filter_by(id=team_id).first()

    def register_topic_transaction(self, team_id, project_id):
        """
        Cập nhật đề tài cho nhóm.
        """
        try:
            team = self.get_team_by_id(team_id)
            if team:
                # [LOGIC]: Cập nhật khóa ngoại project_id
                team.project_id = project_id
                session.commit()
                return team
            return None
        except SQLAlchemyError as e:
            session.rollback()
            raise e