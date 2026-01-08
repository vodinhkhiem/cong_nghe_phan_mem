from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base

class CheckpointModel(Base):
    __tablename__ = 'checkpoints'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    milestone_id = Column(Integer, ForeignKey('project_milestones.id'), nullable=False)
    
    # Trạng thái nộp bài của nhóm cho cột mốc này
    status = Column(String(20), default='Open') # 'Open', 'Submitted', 'Graded', 'Late'
    
    submissions = relationship('Submission', backref='checkpoint', lazy=True)

class SubmissionModel(Base):
    __tablename__ = 'submissions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    checkpoint_id = Column(Integer, ForeignKey('checkpoints.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False) # Người đại diện nộp
    
    file_url = Column(String(255), nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Điểm số và nhận xét từ Giảng viên
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)

class PeerReviewModel(Base):
    __tablename__ = 'peer_reviews'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    reviewer_id = Column(Integer, ForeignKey('users.id'), nullable=False) # Người chấm
    target_id = Column(Integer, ForeignKey('users.id'), nullable=False)   # Người được chấm
    checkpoint_id = Column(Integer, ForeignKey('checkpoints.id'), nullable=False) # Đánh giá ở cột mốc nào
    
    score = Column(Integer, nullable=False) # Thang điểm (VD: 1-5 hoặc 1-10)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())