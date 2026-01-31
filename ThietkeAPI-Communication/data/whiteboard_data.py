# data/whiteboard_data.py

from models.whiteboard import Whiteboard

class WhiteboardData:
    def __init__(self):
        # dict dùng như Hash Table
        # Giải thuật: Hash Map lookup O(1)
        self.whiteboards = {}

        # Khởi tạo dữ liệu mẫu
        self.whiteboards["P001"] = Whiteboard(
            "P001",
            {
                "shapes": ["rectangle", "circle"],
                "texts": ["Sprint goal"]
            }
        )

    def get_state(self, project_id):
        # O(1) average – tra cứu dict
        return self.whiteboards.get(project_id)

    def save_snapshot(self, project_id, new_state):
        # Ghi đè snapshot hiện tại
        self.whiteboards[project_id] = Whiteboard(project_id, new_state)
        return self.whiteboards[project_id]
