# models/whiteboard.py

class Whiteboard:
    def __init__(self, project_id, state):
        # project_id: ID dự án
        # state: JSON state của bảng trắng
        self.project_id = project_id
        self.state = state
