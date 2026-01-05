from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from infrastructure.databases.base import Base

class MessageModel(Base):
    __tablename__ = 'messages'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    
    # Người gửi
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Gửi đến đâu? (Nếu chat nhóm thì có team_id, nếu chat riêng thì receiver_id)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=True)
    receiver_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    content = Column(Text, nullable=False) # Nội dung tin nhắn
    is_read = Column(String(10), default='False') # Đã xem chưa
    
    created_at = Column(DateTime)