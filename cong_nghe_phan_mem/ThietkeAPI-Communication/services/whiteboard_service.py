# services/whiteboard_service.py

from data.whiteboard_data import WhiteboardData

class WhiteboardService:
    def __init__(self):
        self.data = WhiteboardData()

    def get_whiteboard_state(self, project_id):
        """
        API: GET /whiteboards/{projectId}/state
        Lấy JSON state để render lại
        """
        return self.data.get_state(project_id)

    def save_whiteboard_snapshot(self, project_id, state):
        """
        API: POST /whiteboards/{projectId}/snapshot
        Lưu snapshot hiện tại
        """
        return self.data.save_snapshot(project_id, state)
