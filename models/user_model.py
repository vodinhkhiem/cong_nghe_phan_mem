from sqlalchemy import Column, Integer, String, DateTime, Boolean
from infrastructure.databases.base import Base

class UserModel(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    
    # 1. Thông tin đăng nhập
    user_name = Column(String(50), nullable=False, unique=True) # Tên đăng nhập
    password = Column(String(255), nullable=False)              # Mật khẩu Hash (Độ dài 250 như bạn để là Tốt)
    email = Column(String(100), nullable=False, unique=True)    # [MỚI] Email
    
    # 2. Thông tin cá nhân hiển thị lên UI
    full_name = Column(String(100), nullable=True)              # [MỚI] Tên đầy đủ (VD: Nguyen Van A)
    avatar_url = Column(String(500), nullable=True)             # [MỚI] Link ảnh đại diện (cho đẹp UI)
    description = Column(String(255), nullable=True)            # Mô tả/Tiểu sử
    
    # 3. Phân quyền & Trạng thái
    role = Column(String(20), nullable=False, default='Student') # [MỚI] Admin/Lecturer/Student
    status = Column(Boolean, default=True)                       # True = Active (Khớp với cột 'bit' trong ảnh)
    
    created_at = Column(DateTime)
    updated_at = Column(DateTime)