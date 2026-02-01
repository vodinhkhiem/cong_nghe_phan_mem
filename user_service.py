from sqlalchemy.orm import Session
from infrastructure.models import user_model

class UserService:
    @staticmethod
    def get_user_profile(db: Session, user_id: int):
        return db.query(user_model).filter_by(id=user_id).first()

    @staticmethod
    def update_avatar(db: Session, user_id: int, avatar_url: str):
        user = db.query(user_model).filter_by(id=user_id).first()
        if user:
            user.avatar_url = avatar_url
            db.commit()
            return True
        return False