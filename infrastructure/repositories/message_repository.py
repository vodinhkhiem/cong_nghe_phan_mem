from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from infrastructure.models.messager_model import MessageModel
from infrastructure.models.user_model import UserModel

class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, message: MessageModel) -> MessageModel:
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_by_team_id(self, team_id: int, limit: int = 50, offset: int = 0):
        """
        Lấy danh sách tin nhắn, kèm theo thông tin người gửi (Sender).
        Sắp xếp: Mới nhất ở cuối (để hiển thị khung chat từ trên xuống).
        """
        return self.db.query(MessageModel)\
            .options(joinedload(MessageModel.sender)) \
            .filter(MessageModel.team_id == team_id)\
            .order_by(MessageModel.created_at.asc())\
            .limit(limit)\
            .offset(offset)\
            .all()

    def count_by_team(self, team_id: int) -> int:
        """Đếm tổng số tin nhắn (để làm phân trang nếu cần)"""
        return self.db.query(MessageModel).filter(MessageModel.team_id == team_id).count()

    