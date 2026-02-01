# models/whiteboard.py
class Whiteboard:
    def __init__(self, meeting_id):
        self.board_id = meeting_id
        self.state = {
            "shapes": [],
            "texts": []
        }
