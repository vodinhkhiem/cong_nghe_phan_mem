from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func, Boolean, DateTime
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base
from datetime import datetime
from typing import Optional

class TokenBlocklistModel(Base):
    __tablename__ = 'token_blocklist'
    id = Column(Integer, primary_key=True, autoincrement=True)
    jti = Column(String(36), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

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

class MeetingAttendeeModel(Base):
    __tablename__ = 'meeting_attendees'

    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(String(20), default='Pending')
    
    # Quan hệ
    meeting = relationship("MeetingModel", back_populates="attendees")
    user = relationship("UserModel")

class GradeModel(Base):
    __tablename__ = 'grades'
    id = Column(Integer, primary_key=True)
    submission_id = Column(Integer, ForeignKey('submissions.id'))
    score = Column(Float)
    feedback = Column(Text)
    graded_by = Column(Integer, ForeignKey('users.id'))

class AIChatHistoryModel(Base):
    __tablename__ = 'ai_chat_histories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    # 'user' hoặc 'bot'
    sender = Column(String(50), nullable=False) 
    # Nội dung tin nhắn
    message = Column(Text, nullable=False)
    # Gom nhóm các đoạn chat (nếu cần context liên tục)
    conversation_id = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # quan hệ
    user = relationship("UserModel")

class SyllabusModel(Base):
    __tablename__ = 'syllabuses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    content = Column(Text, nullable=True)  # JSON hoặc Text mô tả đề cương
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DocumentModel(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 1. QUAN HỆ VỚI WORKSPACE
    workspace_id = Column(Integer, ForeignKey('workspaces.id'), nullable=False)
    workspace = relationship("WorkspaceModel", back_populates="documents")
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    file_type = Column(String(50), default='CODE')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 2. QUAN HỆ
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
    
    # Lecturer ID (Người đề xuất hoặc người phụ trách)
    lecturer_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Trạng thái: DRAFT (Nháp), PENDING (Chờ duyệt), APPROVED (Đã duyệt), REJECTED
    status = Column(String(20), default='PENDING')
    
    # Quản lý Slot (Tránh Race Condition)
    max_slots = Column(Integer, default=3)     # Tối đa bao nhiêu nhóm được chọn
    current_slots = Column(Integer, default=0) # Hiện tại đã có bao nhiêu nhóm chọn

class TeamRequestModel(Base):
    __tablename__ = 'team_requests'
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Type: 'JOIN' (SV xin vào), 'INVITE' (Leader mời)
    type = Column(String(10), nullable=False) 
    
    # Status: 'PENDING', 'APPROVED', 'REJECTED'
    status = Column(String(20), default='PENDING')

    team = relationship("TeamModel")
    user = relationship("UserModel")

class ProjectModel(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Dự án này đang được thực hiện trong Workspace nào
    workspace_id = Column(Integer, ForeignKey('workspaces.id'), nullable=True)

    # 1. Liên kết với Syllabus
    syllabus_id = Column(Integer, ForeignKey('syllabuses.id'), nullable=False)
    
    # 2. Người tạo
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # 3. Trạng thái duyệt
    status = Column(String(20), default='Pending', nullable=False)
    feedback_from_head = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # === RELATIONSHIPS ===
    #  Khai báo ngược lại với WorkspaceModel
    workspace = relationship("WorkspaceModel", back_populates="projects")
    
    # Milestones 
    milestones = relationship('ProjectMilestoneModel', backref='project', cascade="all, delete-orphan", lazy=True)
    
    # Whiteboard
    whiteboard = relationship("WhiteboardSnapshotModel", back_populates="project", uselist=False, cascade="all, delete-orphan")

class ProjectMilestoneModel(Base):
    __tablename__ = 'project_milestones'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    
    name = Column(String(100), nullable=False) # VD: "Giai đoạn 1: Lên ý tưởng"
    description = Column(Text, nullable=True)
    
    # Hạn nộp bài (tính theo số tuần kể từ khi bắt đầu, hoặc ngày cụ thể)
    deadline = Column(DateTime, nullable=False) 
    # Quan hệ với Checkpoint (Cột mốc thực tế của từng nhóm)
    # checkpoints = relationship('CheckpointModel', backref='milestone', lazy=True)

class NotificationModel(Base):
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False) # Người nhận
    
    title = Column(String(100), nullable=False)
    message = Column(String(255), nullable=False)
    type = Column(String(50), nullable=True) # System, Project, Grade, Chat...
    
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MeetingAttendeeModel(Base):
    __tablename__ = 'meeting_attendees'

    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Trạng thái: 'Pending', 'Present', 'Absent', 'Excused' (Có phép)
    status = Column(String(20), default='Pending')
    
    # Quan hệ
    meeting = relationship("MeetingModel", back_populates="attendees")
    user = relationship("UserModel")