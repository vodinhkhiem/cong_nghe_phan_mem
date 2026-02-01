from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base

class CheckpointModel(Base):
    __tablename__ = 'checkpoints'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    milestone_id = Column(Integer, ForeignKey('project_milestones.id'), nullable=False)
    status = Column(String(20), default='Open') 
    
    # Quan hệ
    submissions = relationship('SubmissionModel', back_populates='checkpoint', cascade="all, delete-orphan")
    peer_reviews = relationship('PeerReviewModel', back_populates='checkpoint', cascade="all, delete-orphan")

class SubmissionModel(Base):
    __tablename__ = 'submissions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    checkpoint_id = Column(Integer, ForeignKey('checkpoints.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False) # Người đại diện nộp
    
    file_url = Column(String(255), nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)

    # Quan hệ
    checkpoint = relationship('CheckpointModel', back_populates='submissions')
    student = relationship('UserModel')

class PeerReviewModel(Base):
    __tablename__ = 'peer_reviews'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    reviewer_id = Column(Integer, ForeignKey('users.id'), nullable=False) # Người chấm
    target_id = Column(Integer, ForeignKey('users.id'), nullable=False)   # Người được chấm
    checkpoint_id = Column(Integer, ForeignKey('checkpoints.id'), nullable=False) # Đánh giá ở cột mốc nào
    
    score = Column(Integer, nullable=False) # Thang điểm (VD: 1-5 hoặc 1-10)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Quan hệ
    checkpoint = relationship('CheckpointModel', back_populates='peer_reviews')
    reviewer = relationship('UserModel', foreign_keys=[reviewer_id])
    target = relationship('UserModel', foreign_keys=[target_id])

class GradeModel(Base):
    __tablename__ = 'grades'
    id = Column(Integer, primary_key=True)
    submission_id = Column(Integer, ForeignKey('submissions.id'))
    score = Column(Float)
    feedback = Column(Text)
    graded_by = Column(Integer, ForeignKey('users.id'))
    