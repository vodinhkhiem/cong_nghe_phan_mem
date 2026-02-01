from typing import List
from sqlalchemy.orm import Session, joinedload
from infrastructure.models.meeting_model import MeetingModel, MeetingAttendeeModel

class MeetingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, meeting: MeetingModel) -> MeetingModel:
        self.db.add(meeting)
        self.db.flush()
        self.db.refresh(meeting)
        return meeting

    def add_attendees(self, attendees: List[MeetingAttendeeModel]):
        """Thêm hàng loạt người tham dự (Bulk Insert) - Tối ưu hiệu năng"""
        self.db.add_all(attendees)

    def get_by_team_id(self, team_id: int):
        """Lấy danh sách cuộc họp của nhóm, kèm số lượng người tham gia"""
        return self.db.query(MeetingModel)\
            .filter(MeetingModel.team_id == team_id)\
            .order_by(MeetingModel.start_time.desc())\
            .all()

    def get_by_id(self, meeting_id: int):
        return self.db.query(MeetingModel)\
            .filter(MeetingModel.id == meeting_id)\
            .first()

    def get_attendee(self, meeting_id: int, user_id: int):
        return self.db.query(MeetingAttendeeModel)\
            .filter(
                MeetingAttendeeModel.meeting_id == meeting_id,
                MeetingAttendeeModel.user_id == user_id
            ).first()

    def update_attendance_status(self, attendee: MeetingAttendeeModel, status: str):
        attendee.status = status
        self.db.commit()
        return attendee

    def update_meeting_notes(self, meeting: MeetingModel, notes: str):
        meeting.meeting_notes = notes
        self.db.commit()
        return meeting