class Meeting:
    def __init__(self, meeting_id, title, location):
        self.meeting_id = meeting_id
        self.title = title
        self.location = location
        self.attendance = {}
        self.notes = ""
