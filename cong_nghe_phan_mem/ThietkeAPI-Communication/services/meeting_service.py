# services/meeting_service.py
# Xử lý API Meeting

from data.meeting_data import MeetingData
from models.meeting import Meeting

class MeetingService:
    def __init__(self):
        self.data = MeetingData()

    # POST /meetings
    def create_meeting(self, meeting_id, title, location):
        meeting = Meeting(meeting_id, title, location)
        return self.data.create(meeting)

    # PUT /meetings/{id}/attendance
    def update_attendance(self, meeting_id, user, status):
        meeting = self.data.find_by_id(meeting_id)
        if meeting:
            meeting.attendance[user] = status
        return meeting

    # PUT /meetings/{id}/notes
    def update_notes(self, meeting_id, notes):
        meeting = self.data.find_by_id(meeting_id)
        if meeting:
            meeting.notes = notes
        return meeting
