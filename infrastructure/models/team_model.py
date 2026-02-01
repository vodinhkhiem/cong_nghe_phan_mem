from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base

class TeamModel(Base):
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('topics.id'), nullable=True) 
    leader_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    class_info = relationship("ClassModel", back_populates="teams")
    
    # Quan hệ
    members = relationship('TeamMemberModel', backref='team', cascade="all, delete-orphan", lazy=True)
    workspace = relationship('WorkspaceModel', uselist=False, backref='team', cascade="all, delete-orphan", lazy=True)
    checkpoints = relationship('CheckpointModel', backref='team', lazy=True)

class TeamMemberModel(Base):
    __tablename__ = 'team_members'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    role = Column(String(20), default='Member') 

class WorkspaceModel(Base):
    __tablename__ = 'workspaces'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    documents = relationship('DocumentModel', back_populates='workspace', cascade="all, delete-orphan", lazy=True)
    projects = relationship("ProjectModel", back_populates="workspace")
    tasks = relationship('TaskModel', backref='workspace', cascade="all, delete-orphan", lazy=True)

class TopicModel(Base):
    __tablename__ = 'topics'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    lecturer_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    status = Column(String(20), default='PENDING')
    
    max_slots = Column(Integer, default=3)     
    current_slots = Column(Integer, default=0)

class TeamRequestModel(Base):
    __tablename__ = 'team_requests'
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    type = Column(String(10), nullable=False) 
    
    status = Column(String(20), default='PENDING')

    team = relationship("TeamModel")
    user = relationship("UserModel")