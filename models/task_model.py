from infrastructure.databases.base import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Text, ForeignKey # Ví dụ các kiểu dữ liệu

class TaskModel(Base):
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 1. Liên kết với Workspace (Bắt buộc)
    # Task phải thuộc về 1 không gian làm việc cụ thể
    workspace_id = Column(Integer, ForeignKey('workspaces.id'), nullable=False)
    
    # 2. Nội dung công việc
    title = Column(String(200), nullable=False) # Tăng độ dài lên 200
    description = Column(Text, nullable=True)   # Dùng Text để viết mô tả dài
    
    # 3. Trạng thái Kanban
    status = Column(String(50), default='To Do', nullable=False) # Giá trị: 'To Do', 'In Progress', 'Done', 'Review'
    
    # 4. Người được phân công
    assignee_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # 5. Hạn chót
    due_date = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    # Quan hệ (Optional - giúp truy vấn ngược dễ hơn)
    # assignee = relationship("UserModel", foreign_keys=[assignee_id])