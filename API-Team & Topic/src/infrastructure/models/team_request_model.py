from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from infrastructure.databases import Base

class TeamRequestModel(Base):
    __tablename__ = 'team_requests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    user_id = Column(Integer, nullable=False) # User liên quan (Người xin vào hoặc Người được mời)
    type = Column(String(50), nullable=False) # 'JOIN' (Xin vào) hoặc 'INVITE' (Mời)
    status = Column(String(50), default='Pending') # Pending, Approved, Rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())