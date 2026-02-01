from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base

class SubjectModel(Base):
    __tablename__ = 'subjects'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False) # Mã môn học, ví dụ: CS101
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Quan hệ
    syllabuses = relationship('SyllabusModel', back_populates='subject', uselist=False)
    classes = relationship('ClassModel', back_populates='subject')
    resources = relationship('ResourceModel', back_populates='subject')

class SyllabusModel(Base):
    __tablename__ = 'syllabuses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    content = Column(Text, nullable=True) 
    clos = Column(Text, nullable=True) 
    grading_scheme = Column(Text, nullable=True) 
    
    # Quan hệ
    subject = relationship("SubjectModel", back_populates="syllabuses")
    projects = relationship("ProjectModel", back_populates="syllabus")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ClassModel(Base):
    __tablename__ = 'classes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)  # Ví dụ: SE1401
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    lecturer_id = Column(Integer, ForeignKey('users.id'))  # Giảng viên phụ trách
    semester = Column(String(20))  # Ví dụ: Fall 2023
    
    # Quan hệ
    subject = relationship('SubjectModel', back_populates='classes')
    students = relationship('ClassMemberModel', back_populates='class_info')
    teams = relationship('TeamModel', back_populates='class_info')

class ClassMemberModel(Base):
    __tablename__ = 'class_members'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey('classes.id'))
    student_id = Column(Integer, ForeignKey('users.id'))

    # Quan hệ
    class_info = relationship('ClassModel', back_populates='students')

class ResourceModel(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    file_url = Column(String)
    type = Column(String) # Document, Video, Link...
    # Link tới Subject hoặc Class
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    uploader_id = Column(Integer, ForeignKey("users.id"))

    # Quan hệ
    subject = relationship("SubjectModel", back_populates="resources")

class RubricModel(Base):
    __tablename__ = 'rubrics'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    content = Column(Text, nullable=False) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())