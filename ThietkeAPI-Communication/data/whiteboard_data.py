# whiteboard_data.py
class WhiteboardRepository:
    def __init__(self):
        self.boards = {}  # key = project_id

    def create(self, project_id):
        self.boards[project_id] = {
            "project_id": project_id,
            "state": {
                "shapes": [],
                "texts": []
            }
        }
        return self.boards[project_id]

    def get_by_project_id(self, project_id):
        return self.boards.get(project_id)

    def save_state(self, project_id, state):
        if project_id in self.boards:
            self.boards[project_id]["state"] = state
