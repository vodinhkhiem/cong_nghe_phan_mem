from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from infrastructure.databases.base import Base

class TodoModel(Base):
    __tablename__ = 'todos'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False) # Pending, In Progress, Done
    
    # --- PHẦN BỔ SUNG QUAN TRỌNG ---
    # Task này của ai tạo?
    creator_id = Column(Integer, ForeignKey('flask_user.id'), nullable=False)
    # Task này thuộc nhóm nào? (Nếu là task cá nhân thì để Null)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=True)
    # Ai được giao làm task này?
    assignee_id = Column(Integer, ForeignKey('flask_user.id'), nullable=True)

    deadline = Column(DateTime, nullable=True) # Nên có thêm Deadline
    created_at = Column(DateTime)
    updated_at = Column(DateTime)