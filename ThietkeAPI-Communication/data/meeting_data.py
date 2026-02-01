# data/meeting_data.py
# Lưu trữ dữ liệu cuộc họp

from models.meeting import Meeting

class MeetingData:
    def __init__(self):
        self.meetings = []

    # POST /meetings
    def create(self, meeting):
        self.meetings.append(meeting)
        return meeting

    # Linear Search – O(n)
    def find_by_id(self, meeting_id):
        for m in self.meetings:
            if m.meeting_id == meeting_id:
                return m
        return None
