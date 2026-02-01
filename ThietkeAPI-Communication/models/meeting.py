class Meeting:
    def __init__(self, meeting_id, title, location, project_id=None):
        self.meeting_id = meeting_id
        self.title = title
        self.location = location
        self.project_id = project_id or f"P_{meeting_id}"
        self.attendance = {}
        self.notes = ""
