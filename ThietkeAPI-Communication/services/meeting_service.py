from repositories.meeting_repository import MeetingRepository
from models.meeting import Meeting

class MeetingService:
    def __init__(self, whiteboard_service):
        self.meeting_repo = MeetingRepository()
        self.whiteboard_service = whiteboard_service

    def create_meeting(self, meeting_id, title, location):
        meeting = Meeting(meeting_id, title, location)
        self.meeting_repo.save(meeting)
        return meeting

    def join_meeting(self, meeting_id, use_whiteboard=False):
        meeting = self.meeting_repo.get_by_id(meeting_id)

        response = {
            "meeting_id": meeting.meeting_id,
            "project_id": meeting.project_id,
            "has_whiteboard": False
        }

        if use_whiteboard:
            self.whiteboard_service.create_board(meeting.project_id)
            response["has_whiteboard"] = True

        return response
