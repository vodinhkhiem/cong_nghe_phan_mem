class WhiteboardRepository:
    def __init__(self):
        # key: project_id, value: state (dict)
        self.boards = {}

    def create(self, project_id):
        if project_id not in self.boards:
            self.boards[project_id] = {}

    def get_state(self, project_id):
        return self.boards.get(project_id, {})

    def save_snapshot(self, project_id, state):
        self.boards[project_id] = state
