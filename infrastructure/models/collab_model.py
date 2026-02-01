from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base 
from datetime import datetime
from typing import Optional

class DocumentModel(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    workspace_id = Column(Integer, ForeignKey('workspaces.id'), nullable=False)
    workspace = relationship("WorkspaceModel", back_populates="documents")
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    file_type = Column(String(50), default='CODE')
    
    # Tracking thời gian
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # quan hệ
    last_updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    last_editor = relationship("UserModel")

class WhiteboardSnapshotModel(Base):
    __tablename__ = 'whiteboard_snapshots'

    project_id = Column(Integer, ForeignKey('projects.id'), primary_key=True)
    project = relationship("ProjectModel", back_populates="whiteboard")
    data = Column(Text, nullable=False, default="{}") 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Whiteboard Project={self.project_id} Updated At={self.updated_at}>"