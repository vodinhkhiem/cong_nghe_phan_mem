from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base 

# 1. Bảng lưu trữ Tài liệu (Code & Báo cáo)
class DocumentModel(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    workspace_id = Column(Integer, ForeignKey('workspaces.id'), nullable=False)
    
    name = Column(String(255), nullable=False)      # VD: "Main.java", "Chapter1.docx"
    content = Column(Text, nullable=True)           # Nội dung file (Lưu text hoặc JSON)
    file_type = Column(String(50), default='CODE')  # 'CODE', 'DOC', 'MARKDOWN'
    
    # Tracking thời gian để biết ai sửa cuối cùng
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Quan hệ ngược (Optional)
    # workspace = relationship("WorkspaceModel", back_populates="documents")

# 2. Bảng lưu trữ trạng thái Bảng trắng (Whiteboard)
class WhiteboardSnapshotModel(Base):
    __tablename__ = 'whiteboard_snapshots'

    id = Column(Integer, primary_key=True, autoincrement=True)
    workspace_id = Column(Integer, ForeignKey('workspaces.id'), nullable=False)
    
    data = Column(Text, nullable=False) # Lưu chuỗi JSON khổng lồ của các nét vẽ
    created_at = Column(DateTime(timezone=True), server_default=func.now())