from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base

class TeamModel(Base):
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True) # Nhóm làm dự án nào
    leader_id = Column(Integer, ForeignKey('users.id'), nullable=True) # Trưởng nhóm
    
    # Quan hệ
    members = relationship('TeamMember', backref='team', cascade="all, delete-orphan", lazy=True)
    # Mỗi team có 1 Workspace duy nhất (uselist=False)
    workspace = relationship('Workspace', uselist=False, backref='team', cascade="all, delete-orphan", lazy=True)
    checkpoints = relationship('Checkpoint', backref='team', lazy=True)

class TeamMemberModel(Base):
    __tablename__ = 'team_members'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    role = Column(String(20), default='Member') # 'Leader' hoặc 'Member'

class WorkspaceModel(Base):
    __tablename__ = 'workspaces'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False, unique=True)
    
    # Lưu dữ liệu thời gian thực (JSON String)
    whiteboard_data = Column(Text, nullable=True) 
    document_content = Column(Text, nullable=True)
    
    tasks = relationship('Task', backref='workspace', lazy=True)
