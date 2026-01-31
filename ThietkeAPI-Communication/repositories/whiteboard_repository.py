from models.whiteboard import Whiteboard
class WhiteboardRepository:
    _boards = {}

    def create(self, meeting_id):
        if meeting_id not in self._boards:
            board = Whiteboard(meeting_id)
            self._boards[meeting_id] = board
        return self._boards[meeting_id]

    def get_by_meeting_id(self, meeting_id):
        return self._boards.get(meeting_id)

    def save_state(self, meeting_id, state):
        board = self.get_by_meeting_id(meeting_id)
        if not board:
            raise Exception("Whiteboard not found")
        board.state = state
        return board
