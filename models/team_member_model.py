from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from infrastructure.databases.base import Base

class TeamMemberModel(Base):
    __tablename__ = 'team_members'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    
    # Liên kết User và Team
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Vai trò trong nhóm (Member, Vice Leader...)
    role = Column(String(50), default='Member')
    
    joined_at = Column(DateTime)