from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from infrastructure.databases.base import Base
from sqlalchemy.orm import relationship

class MessageModel(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False) 
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False) 
    type = Column(String(20), default='TEXT') 
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sender = relationship("UserModel")