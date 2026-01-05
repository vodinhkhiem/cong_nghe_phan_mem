from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from infrastructure.databases.base import Base

class SubmissionModel(Base):
    __tablename__ = 'submissions'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    
    # Nộp cho Task nào? (Liên kết với bảng todos)
    todo_id = Column(Integer, ForeignKey('todos.id'), nullable=False)
    
    # Ai nộp? (Sinh viên)
    student_id = Column(Integer, ForeignKey('flask_user.id'), nullable=False)
    
    file_url = Column(String(500), nullable=True) # Link file (PDF, Zip...)
    content = Column(Text, nullable=True)         # Nội dung text (nếu có)
    
    submitted_at = Column(DateTime) # Thời gian nộp (để check trễ deadline)
    
    # Trạng thái nộp (VD: "Submitted", "Late", "Graded")
    status = Column(String(50), default='Submitted')