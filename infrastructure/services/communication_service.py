from sqlalchemy.orm import Session
from datetime import datetime

# Import Models
from infrastructure.models.messager_model import MessageModel
from infrastructure.models.meeting_model import MeetingModel, MeetingAttendeeModel
from infrastructure.models.team_model import TeamModel, TeamMemberModel

# Import Repositories
from infrastructure.repositories.message_repository import MessageRepository
from infrastructure.repositories.meeting_repository import MeetingRepository

class CommunicationService:
    
    # CHAT SERVICE
    @staticmethod
    def get_user_conversations(db: Session, user_id: int):
        return db.query(TeamModel).join(TeamMemberModel).filter(TeamMemberModel.user_id == user_id).all()

    @staticmethod
    def get_messages(db: Session, team_id: int, limit: int = 50):
        repo = MessageRepository(db)
        return repo.get_by_team_id(team_id, limit)

    @staticmethod
    def send_message(db: Session, team_id: int, sender_id: int, content: str, msg_type: str = 'TEXT'):
        repo = MessageRepository(db)
        new_msg = MessageModel(
            team_id=team_id,
            sender_id=sender_id,
            content=content,
            type=msg_type
        )
        return repo.create(new_msg)

    # MEETING SERVICE
    @staticmethod
    def create_meeting(db: Session, data: dict, creator_id: int):
        meeting_repo = MeetingRepository(db)
        
        try:
            # 1. Tạo Header cuộc họp
            new_meeting = MeetingModel(
                team_id=data.get('team_id'),
                creator_id=creator_id,
                title=data.get('title'),
                description=data.get('description'),
                start_time=datetime.fromisoformat(data.get('start_time')),
                end_time=datetime.fromisoformat(data.get('end_time')),
                location=data.get('location'),
                meeting_link=data.get('meeting_link'),
                is_online=data.get('is_online', True)
            )
            saved_meeting = meeting_repo.create(new_meeting)

            # 2. Logic: Lấy thành viên để thêm vào cuộc họp
            members = db.query(TeamMemberModel).filter_by(team_id=data.get('team_id')).all()
            
            # Tạo list attendees từ members
            attendees = []
            for mem in members:
                attendees.append(MeetingAttendeeModel(
                    meeting_id=saved_meeting.id,
                    user_id=mem.user_id,
                    status='Pending'
                ))
            
            # Bulk insert người tham gia
            meeting_repo.add_attendees(attendees) 

            # 3. CHỐT SỔ (COMMIT) TẠI ĐÂY
            db.commit() 
            
            return saved_meeting

        except Exception as e:
            db.rollback() 
            raise e 

    @staticmethod
    def get_team_meetings(db: Session, team_id: int):
        repo = MeetingRepository(db)
        return repo.get_by_team_id(team_id)

    @staticmethod
    def mark_attendance(db: Session, meeting_id: int, user_id: int, status: str):
        repo = MeetingRepository(db)
        attendee = repo.get_attendee(meeting_id, user_id)
        
        if attendee:
            repo.update_attendance_status(attendee, status)
            return True
        return False

    @staticmethod
    def update_notes(db: Session, meeting_id: int, notes: str):
        repo = MeetingRepository(db)
        meeting = repo.get_by_id(meeting_id)
        
        if meeting:
            repo.update_meeting_notes(meeting, notes)
            return True
        return False