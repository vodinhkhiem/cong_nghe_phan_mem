from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base 
from datetime import datetime
from typing import Optional

# 1. Bảng lưu trữ Tài liệu (Code & Báo cáo)
class DocumentModel(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    workspace_id = Column(Integer, ForeignKey('workspaces.id'), nullable=False)
    # VD: "Main.java", "Chapter1.docx"
    name: str = Column(String(255), nullable=False) # type: ignore
    # Nội dung file (Lưu text hoặc JSON)
    content: str = Column(Text, nullable=True) # type: ignore
    # 'CODE', 'DOC', 'MARKDOWN'
    file_type: str = Column(String(50), default='CODE') # type: ignore
    
    # Tracking thời gian để biết ai sửa cuối cùng
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), onupdate=func.now()) # type: ignore

    # Quan hệ ngược (Optional)
    # workspace = relationship("WorkspaceModel", back_populates="documents")

# 2. Bảng lưu trữ trạng thái Bảng trắng (Whiteboard)
class WhiteboardSnapshotModel(Base):
    __tablename__ = 'whiteboard_snapshots'

    id = Column(Integer, primary_key=True, autoincrement=True)
    workspace_id = Column(Integer, ForeignKey('workspaces.id'), nullable=False)
    # Lưu chuỗi JSON khổng lồ của các nét vẽ
    data: str = Column(Text, nullable=False) # type: ignore
    created_at = Column(DateTime(timezone=True), server_default=func.now())