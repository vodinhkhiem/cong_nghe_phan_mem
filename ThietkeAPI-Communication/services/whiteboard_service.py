from repositories.whiteboard_repository import WhiteboardRepository

class WhiteboardService:
    def __init__(self):
        self.repo = WhiteboardRepository()

    def create_board(self, project_id):
        self.repo.create(project_id)

    def get_state(self, project_id):
        return self.repo.get_state(project_id)

    def save_snapshot(self, project_id, state):
        self.repo.save_snapshot(project_id, state)
