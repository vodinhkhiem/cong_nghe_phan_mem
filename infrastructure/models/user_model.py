from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, func
from infrastructure.databases.base import Base
import datetime

class UserModel(Base):
    __tablename__ = 'users'
    # __table_args__ = {'extend_existing': True}  # Thêm dòng này nếu cần mở rộng bảng đã tồn tại
    id = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(258), nullable=False)
    role = Column(String(20), nullable=False, default='Student')
    avatar_url = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    status = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 
    reset_token = Column(String(100), nullable=True)
    reset_token_expiry = Column(DateTime, nullable=True)

class TokenBlocklistModel(Base):
    __tablename__ = 'token_blocklist'
    id = Column(Integer, primary_key=True, autoincrement=True)
    jti = Column(String(36), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)