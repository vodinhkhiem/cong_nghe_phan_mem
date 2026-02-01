from sqlalchemy.orm import Session
from infrastructure.models import user_model

class AuthService:
    @staticmethod
    def register_user(db: Session, data: dict):
        # Kiểm tra trùng email
        user = db.query(user_model).filter_by(email=data['email']).first()
        if user:
            return None, "Email đã tồn tại."
        
        new_user = user_model(
            full_name=data.get('full_name'),
            email=data.get('email'),
            password=data.get('password'),
            role='Student' # Mặc định cho sinh viên
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user, "Thành công"

    @staticmethod
    def authenticate(db: Session, email, password):
        # Xác thực logic đăng nhập
        return db.query(user_model).filter_by(email=email, password=password).first()