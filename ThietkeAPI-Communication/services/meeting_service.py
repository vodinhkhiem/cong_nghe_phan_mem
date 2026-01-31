from repositories.meeting_repository import MeetingRepository
from services.whiteboard_service import WhiteboardService


class MeetingService:
    def __init__(self):
        self.repo = MeetingRepository()
        self.whiteboard_service = WhiteboardService()

    # ======================
    # CREATE MEETING
    # ======================
    def create_meeting(self, meeting_id, title, location):
        meeting = self.repo.create(meeting_id, title, location)
        return meeting

    # ======================
    # UPDATE ATTENDANCE
    # ======================
    def update_attendance(self, meeting_id, student_id, status):
        meeting = self.repo.get_by_id(meeting_id)
        if not meeting:
            raise Exception("Meeting not found")

        meeting.attendance[student_id] = status
        return meeting.attendance

    # ======================
    # UPDATE NOTES
    # ======================
    def update_notes(self, meeting_id, notes):
        meeting = self.repo.get_by_id(meeting_id)
        if not meeting:
            raise Exception("Meeting not found")

        meeting.notes = notes
        return meeting.notes

    # ======================
    # JOIN MEETING (+ WHITEBOARD)
    # ======================
    def join_meeting(self, meeting_id, use_whiteboard=False):
        meeting = self.repo.get_by_id(meeting_id)
        if not meeting:
            raise Exception("Meeting not found")

        response = {
            "meeting_id": meeting.meeting_id,
            "title": meeting.title,
            "has_whiteboard": False
        }

        print(f"Joined meeting {meeting.meeting_id}")

        if use_whiteboard:
            board = self.whiteboard_service.create_board(meeting_id)
            response["has_whiteboard"] = True
            response["whiteboard_id"] = board.board_id
            print("Whiteboard activated:", board.board_id)

        return response
