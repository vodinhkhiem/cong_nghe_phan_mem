from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, func
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base

class MeetingModel(Base):
    __tablename__ = 'meetings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 1. Liên kết: Cuộc họp này của Nhóm nào? (Có thể null nếu là cuộc họp chung)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=True)
    
    # 2. Ai là người tạo lịch họp? (Leader hoặc Lecturer)
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True) # Nội dung cuộc họp
    
    # 3. Thời gian bắt đầu & kết thúc
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    
    # 4. Địa điểm hoặc Link Online
    meeting_link = Column(String(500), nullable=True) # Link Google Meet / Zoom
    location = Column(String(200), nullable=True)     # Phòng học vật lý
    
    # Cờ đánh dấu: Cuộc họp online hay offline
    is_online = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())