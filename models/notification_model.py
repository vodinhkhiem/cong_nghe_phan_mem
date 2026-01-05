from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from infrastructure.databases.base import Base

class NotificationModel(Base):
    __tablename__ = 'notifications'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    
    # Thông báo cho ai?
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    title = Column(String(255), nullable=False)
    message = Column(String(500), nullable=False)
    type = Column(String(50)) # VD: 'System', 'Deadline', 'Grade'
    is_read = Column(Boolean, default=False)
    
    created_at = Column(DateTime)