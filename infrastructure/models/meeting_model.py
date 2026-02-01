from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, func
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base

class MeetingModel(Base):
    __tablename__ = 'meetings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=True)
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True) 
    
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    
    meeting_link = Column(String(500), nullable=True) 
    location = Column(String(200), nullable=True)   
    is_online = Column(Boolean, default=True)
    meeting_notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Quan hệ
    attendees = relationship("MeetingAttendeeModel", back_populates="meeting", cascade="all, delete-orphan")

class MeetingAttendeeModel(Base):
    __tablename__ = 'meeting_attendees'

    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(String(20), default='Pending')
    
    # Quan hệ
    meeting = relationship("MeetingModel", back_populates="attendees")
    user = relationship("UserModel")