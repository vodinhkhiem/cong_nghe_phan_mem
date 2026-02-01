from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from infrastructure.databases import Base

class TopicModel(Base):
    __tablename__ = 'topics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(String(500))
    created_by = Column(Integer, nullable=False) # ID người tạo (GV hoặc SV)
    is_suggested_by_gv = Column(Boolean, default=False) # True: Đề tài do GV đề xuất
    status = Column(String(50), default='Pending') # Pending (Chờ duyệt), Approved (Đã duyệt), Rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())