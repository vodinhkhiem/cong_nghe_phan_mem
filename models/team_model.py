from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from infrastructure.databases.base import Base

class TeamModel(Base):
    __tablename__ = 'teams'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    team_name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    
    # Nhóm này thuộc về Lớp học/Khóa học nào?
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    # Ai là trưởng nhóm? (Liên kết với bảng users)
    leader_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    created_at = Column(DateTime)
    updated_at = Column(DateTime)