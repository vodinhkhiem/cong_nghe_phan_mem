from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey
from infrastructure.databases.base import Base

class NotificationModel(Base):
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False) # Người nhận
    
    title = Column(String(100), nullable=False)
    message = Column(String(255), nullable=False)
    type = Column(String(50), nullable=True) # System, Project, Grade, Chat...
    
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    