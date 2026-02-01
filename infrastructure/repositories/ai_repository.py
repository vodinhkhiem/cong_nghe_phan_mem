from sqlalchemy.orm import Session
from infrastructure.models.ai_model import AIChatHistoryModel
from infrastructure.models.task_model import TaskModel
from typing import List

class AIRepository:
    def __init__(self, session: Session):
        self.session = session

    def save_chat_log(self, user_id: int, sender: str, message: str, conversation_id: str = None):
        log = AIChatHistoryModel(
            user_id=user_id,
            sender=sender,
            message=message,
            conversation_id=conversation_id
        )
        self.session.add(log)
        self.session.commit()
        return log

    def get_history_by_user(self, user_id: int, limit: int = 50) -> List[AIChatHistoryModel]:
        return self.session.query(AIChatHistoryModel)\
            .filter_by(user_id=user_id)\
            .order_by(AIChatHistoryModel.created_at.desc())\
            .limit(limit)\
            .all()

    def get_task_by_id(self, task_id: int):
        return self.session.query(TaskModel).filter_by(id=task_id).first()