from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base

class ProjectModel(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    workspace_id = Column(Integer, ForeignKey('workspaces.id'), nullable=True)
    syllabus_id = Column(Integer, ForeignKey('syllabuses.id'), nullable=False)
    
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    status = Column(String(20), default='Pending', nullable=False)
    feedback_from_head = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # quan hệ
    workspace = relationship("WorkspaceModel", back_populates="projects")
    syllabus = relationship("SyllabusModel", back_populates="projects")
    milestones = relationship('ProjectMilestoneModel', backref='project', cascade="all, delete-orphan", lazy=True)
    whiteboard = relationship("WhiteboardSnapshotModel", back_populates="project", uselist=False, cascade="all, delete-orphan")

class ProjectMilestoneModel(Base):
    __tablename__ = 'project_milestones'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    deadline = Column(DateTime, nullable=False) 
    # Quan hệ với Checkpoint (Cột mốc thực tế của từng nhóm)
    # checkpoints = relationship('CheckpointModel', backref='milestone', lazy=True)