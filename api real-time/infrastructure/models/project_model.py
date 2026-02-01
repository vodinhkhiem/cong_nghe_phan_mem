from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base

class ProjectModel(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 1. Liên kết với Syllabus: Dự án này thuộc môn nào, đề cương nào
    syllabus_id = Column(Integer, ForeignKey('syllabuses.id'), nullable=False)
    
    # 2. Người tạo: Thường là Lecturer
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # 3. Trạng thái duyệt của Head Dept
    status = Column(String(20), default='Pending', nullable=False) # 'Pending' (Chờ duyệt), 'Approved' (Đã duyệt), 'Denied' (Từ chối)
    
    # Phản hồi từ Head Dept nếu từ chối hoặc yêu cầu chỉnh sửa
    feedback_from_head = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # QUAN HỆ:
    # Một dự án có nhiều cột mốc
    milestones = relationship('ProjectMilestoneModel', backref='project', cascade="all, delete-orphan", lazy=True)
    # Một dự án có thể được gán cho nhiều lớp (Thông qua bảng trung gian ProjectAllocation - sẽ tạo sau hoặc dùng quan hệ 1-n)
    # teams = relationship('TeamModel', backref='project', lazy=True)

class ProjectMilestoneModel(Base):
    __tablename__ = 'project_milestones'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    
    name = Column(String(100), nullable=False) # VD: "Giai đoạn 1: Lên ý tưởng"
    description = Column(Text, nullable=True)
    
    # Hạn nộp bài (tính theo số tuần kể từ khi bắt đầu, hoặc ngày cụ thể)
    due_week = Column(Integer, nullable=True) # VD: Tuần thứ 3
    # Quan hệ với Checkpoint (Cột mốc thực tế của từng nhóm)
    # checkpoints = relationship('CheckpointModel', backref='milestone', lazy=True)