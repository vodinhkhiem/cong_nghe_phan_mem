from models.meeting import Meeting


class MeetingRepository:
    def __init__(self):
        self.meetings = {}

    def create(self, meeting_id, title, location):
        meeting = Meeting(meeting_id, title, location)
        self.meetings[meeting_id] = meeting
        return meeting

    def get_by_id(self, meeting_id):
        return self.meetings.get(meeting_id)
