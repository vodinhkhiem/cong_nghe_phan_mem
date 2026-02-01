import bcrypt
import jwt
import datetime
import uuid
from infrastructure.models.user_model import UserModel
from infrastructure.repositories.user_repository import UserRepository
from api.constants import SECRET_KEY, ALGORITHM

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.repo = user_repo

    def register(self, full_name, email, password, role='Student'):
        if self.repo.get_by_email(email):
            raise ValueError("Email đã tồn tại")
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = UserModel(
            full_name=full_name,
            email=email,
            password=hashed_pw,
            role=role,
            status= True
        )
        return self.repo.create(new_user)

    def login(self, email, password):
        user = self.repo.get_by_email(email)
        if not user:
            raise ValueError("Email hoặc mật khẩu không đúng")

        if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            raise ValueError("Email hoặc mật khẩu không đúng")

        # Tạo Access Token
        access_payload = {
            "sub": str(user.id),
            "role": user.role,
            "type": "access",
            "jti": str(uuid.uuid4()),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }
        # Dùng SECRET_KEY và ALGORITHM lấy từ file constants
        access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)

        # Tạo Refresh Token
        refresh_payload = {
            "sub": str(user.id),
            "type": "refresh",
            "jti": str(uuid.uuid4()),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }
        refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm=ALGORITHM)
        
        return {
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "user": {"id": user.id, "name": user.full_name, "role": user.role}
        }
    def refresh_token(self, refresh_token):
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload['type'] != 'refresh':
                raise ValueError("Token không hợp lệ")
            
            if self.repo.is_token_blocked(payload['jti']):
                raise ValueError("Token đã bị hủy")

            user = self.repo.get_by_id(payload['sub'])
            if not user:
                raise ValueError("User không tồn tại")

            new_access_payload = {
                "sub": str(user.id),
                "role": user.role,
                "type": "access",
                "jti": str(uuid.uuid4()),
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            }
            return jwt.encode(new_access_payload, SECRET_KEY, algorithm=ALGORITHM)
        except jwt.ExpiredSignatureError:
            raise ValueError("Refresh token đã hết hạn, vui lòng đăng nhập lại")
        except Exception:
            raise ValueError("Token không hợp lệ")

    def logout(self, token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            jti = payload.get('jti')
            if jti:
                self.repo.add_token_to_blocklist(jti)
                return True
        except:
            pass 
        return False

    def forgot_password(self, email):
        user = self.repo.get_by_email(email)
        if not user:
            return 

        reset_token = str(uuid.uuid4())
        self.repo.save_reset_token(user.id, reset_token)

        # GIẢ LẬP GỬI EMAIL
        print(f"\n[EMAIL MOCK] Gửi tới {email}: Link reset password là /reset-password?token={reset_token}\n")

    def reset_password(self, token, new_password):
        user = self.repo.get_by_reset_token(token)
        if not user:
            raise ValueError("Mã xác thực không hợp lệ hoặc đã hết hạn")

        hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user.password = hashed_pw
        user.reset_token = None 
        user.reset_token_expiry = None
        self.repo.update(user)