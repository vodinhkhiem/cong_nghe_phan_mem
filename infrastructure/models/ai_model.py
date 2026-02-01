from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base

class AIChatHistoryModel(Base):
    __tablename__ = 'ai_chat_histories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    # 'user' hoặc 'bot'
    sender = Column(String(50), nullable=False) 
    # Nội dung tin nhắn
    message = Column(Text, nullable=False)
    # Gom nhóm các đoạn chat (nếu cần context liên tục)
    conversation_id = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # quan hệ
    user = relationship("UserModel")