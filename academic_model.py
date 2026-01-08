from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base

class SubjectModel(Base):
    __tablename__ = 'subjects'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False) # Mã môn học, ví dụ: CS101
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Quan hệ ngược để truy cập từ Syllabus
    syllabuses = relationship('Syllabus', backref='subject', lazy=True)

class SyllabusModel(Base):
    __tablename__ = 'syllabuses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    content = Column(Text, nullable=True)  # JSON hoặc Text mô tả đề cương
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ClassModel(Base):
    __tablename__ = 'classes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)  # Ví dụ: SE1401
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    lecturer_id = Column(Integer, ForeignKey('users.id'))  # Giảng viên phụ trách
    semester = Column(String(20))  # Ví dụ: Fall 2023
    
    # Quan hệ
    students = relationship('ClassMember', backref='class_info', lazy=True)
    # teams sẽ được định nghĩa trong model Team, dùng backref ở đó để liên kết ngược
    teams = relationship('Team', backref='class_info', lazy=True)

class ClassMemberModel(Base):
    __tablename__ = 'class_members'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey('classes.id'))
    student_id = Column(Integer, ForeignKey('users.id'))  # Sinh viên tham gia lớp