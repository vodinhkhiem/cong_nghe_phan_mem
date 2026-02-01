from sqlalchemy.orm import Session
from infrastructure.models.user_model import UserModel, TokenBlocklistModel
import datetime
from typing import Optional

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_email(self, email: str) -> Optional[UserModel]:
        return self.session.query(UserModel).filter_by(email=email).first()

    def get_by_id(self, user_id: int) -> Optional[UserModel]:
        return self.session.query(UserModel).filter_by(id=user_id).first()

    def create(self, user: UserModel) -> UserModel:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def update(self, user: UserModel):
        self.session.commit()
        self.session.refresh(user)
        return user

    def add_token_to_blocklist(self, jti: str):
        token = TokenBlocklistModel(jti=jti)
        self.session.add(token)
        self.session.commit()

    def is_token_blocked(self, jti: str) -> bool:
        return self.session.query(TokenBlocklistModel).filter_by(jti=jti).first() is not None

    def save_reset_token(self, user_id, token):
        user = self.get_by_id(user_id)
        if user:
            user.reset_token = token
            # Token hết hạn sau 15 phút
            user.reset_token_expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
            self.session.commit()
            return True
        return False

    def get_by_reset_token(self, token: str):
        # Tìm user có token khớp và chưa hết hạn
        return self.session.query(UserModel).filter(
            UserModel.reset_token == token,
            UserModel.reset_token_expiry > datetime.datetime.utcnow()
        ).first()