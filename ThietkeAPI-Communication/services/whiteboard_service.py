from repositories.whiteboard_repository import WhiteboardRepository

class WhiteboardService:
    def __init__(self):
        self.repo = WhiteboardRepository()

    # POST /whiteboards/{id}
    def create_board(self, meeting_id):
        return self.repo.create(meeting_id)

    # GET /whiteboards/{id}/state
    def get_state(self, meeting_id):
        board = self.repo.get_by_meeting_id(meeting_id)
        if not board:
            raise Exception("Whiteboard not found")
        return board.state

    # POST /whiteboards/{id}/snapshot
    def save_snapshot(self, meeting_id, state):
        return self.repo.save_state(meeting_id, state)
