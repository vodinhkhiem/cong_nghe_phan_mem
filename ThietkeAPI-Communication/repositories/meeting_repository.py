class MeetingRepository:
    def __init__(self):
        self.meetings = {}

    def save(self, meeting):
        self.meetings[meeting.meeting_id] = meeting

    def get_by_id(self, meeting_id):
        return self.meetings.get(meeting_id)
