from infrastructure.databases.base import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Text, ForeignKey # Ví dụ các kiểu dữ liệu

class TaskModel(Base):
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    workspace_id = Column(Integer, ForeignKey('workspaces.id'), nullable=False)
    title = Column(String(200), nullable=False) 
    description = Column(Text, nullable=True)  
    
    status = Column(String(50), default='To Do', nullable=False) 
    position = Column(Integer, default=0)
    assignee_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    due_date = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    priority = Column(String(20), default='Medium') 

    # quan hệ
    assignee = relationship("UserModel")
    checklists = relationship("TaskChecklistModel", back_populates="task", cascade="all, delete-orphan")
    activities = relationship("TaskActivityModel", back_populates="task", cascade="all, delete-orphan")
    comments = relationship("TaskCommentModel", back_populates="task", cascade="all, delete-orphan")
    attachments = relationship("TaskAttachmentModel", back_populates="task", cascade="all, delete-orphan")

class TaskChecklistModel(Base):
    __tablename__ = 'task_checklists'
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    content = Column(String(500), nullable=False)
    is_done = Column(Boolean, default=False)
    task = relationship("TaskModel", back_populates="checklists")

class TaskActivityModel(Base):
    __tablename__ = 'task_activities'
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String(500)) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    task = relationship("TaskModel", back_populates="activities")
    user = relationship("UserModel")

class TaskCommentModel(Base):
    __tablename__ = 'task_comments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("UserModel")
    task = relationship("TaskModel", back_populates="comments")

class TaskAttachmentModel(Base):
    __tablename__ = 'task_attachments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    url = Column(String(500), nullable=False)
    name = Column(String(255))
    task = relationship("TaskModel", back_populates="attachments")