from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from infrastructure.databases.base import Base

class MessageModel(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False) # Chat trong team nào
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False) # Người gửi
    
    content = Column(Text, nullable=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())