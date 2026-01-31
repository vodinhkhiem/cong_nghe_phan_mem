from sqlalchemy.exc import SQLAlchemyError
from infrastructure.databases.mssql import session
from infrastructure.models.team_model import TeamModel
from infrastructure.models.team_member_model import TeamMemberModel

class TeamRepository:
    def create_team_with_transaction(self, name, class_id, leader_id):
        """
        [ALGORITHM]: ACID Transaction (Atomicity)
        Mục đích: Đảm bảo tính toàn vẹn dữ liệu. 
        Nếu việc thêm Leader thất bại, việc tạo Team cũng phải bị hủy (Rollback).
        """
        try:
            # 1. Start Transaction
            new_team = TeamModel(name=name, class_id=class_id, leader_id=leader_id)
            session.add(new_team)
            session.flush() # Flush để lấy ID của team vừa tạo ngay lập tức

            # 2. Insert TeamMember (Gán role Leader)
            new_member = TeamMemberModel(
                team_id=new_team.id,
                user_id=leader_id,
                role='Leader'
            )
            session.add(new_member)
            
            # [CHECKPOINT]: Nếu cả 2 bước trên không lỗi, mới Commit vào DB
            session.commit()
            return new_team
        except SQLAlchemyError as e:
            # [ROLLBACK]: Hoàn tác mọi thay đổi nếu có lỗi
            session.rollback()
            raise e

    def get_team_by_id(self, team_id):
        return session.query(TeamModel).filter_by(id=team_id).first()

    def register_topic_transaction(self, team_id, project_id):
        """
        [ALGORITHM]: Optimistic Locking (Implicit via Transaction)
        Mục đích: Cập nhật đề tài cho nhóm an toàn, tránh xung đột dữ liệu.
        """
        try:
            team = self.get_team_by_id(team_id)
            if team:
                team.project_id = project_id
                session.commit() # Chốt transaction
                return team
            return None
        except SQLAlchemyError as e:
            session.rollback()
            raise e