import unittest
from services.chat_service import ChatService
from services.meeting_service import MeetingService
from services.whiteboard_service import WhiteboardService

class TestCommunicationAPI(unittest.TestCase):

    def test_send_message(self):
        chat = ChatService()
        msg = chat.send_message("C001", "user2", "Hello")
        self.assertEqual(msg.content, "Hello")

    def test_create_meeting(self):
        meeting_service = MeetingService()
        meeting = meeting_service.create_meeting("M001", "Sprint", "Online")
        self.assertEqual(meeting.title, "Sprint")

    def test_whiteboard_state(self):
        wb = WhiteboardService()
        wb.create_board("P001")
        state = wb.get_state("P001")
        self.assertIsInstance(state, dict)

if __name__ == "__main__":
    unittest.main()
