# main.py
# Demo toàn bộ API Communication

from services.chat_service import ChatService
from services.meeting_service import MeetingService

# ===== CHAT =====
chat_service = ChatService()

print("=== GET Conversations ===")
for c in chat_service.get_conversations():
    print("-", c.conversation_id, c.participants)

print("\n=== GET Messages ===")
for m in chat_service.get_messages("C001"):
    print(f"{m.sender}: {m.content}")

print("\n=== SEND Message ===")
sent = chat_service.send_message("C001", "user2", "Hi, I received your message")
print("Sent:", sent.content)

print("\n=== Messages After Sending ===")
for m in chat_service.get_messages("C001"):
    print(f"{m.sender}: {m.content}")

# ===== MEETING =====
meeting_service = MeetingService()

print("\n=== CREATE MEETING ===")
meeting = meeting_service.create_meeting(
    "M001",
    "Sprint Planning",
    "Google Meet"
)
print("Meeting ID:", meeting.meeting_id)
print("Title:", meeting.title)
print("Location:", meeting.location)

print("\n=== UPDATE ATTENDANCE ===")
meeting_service.update_attendance("M001", "SV01", "Present")
meeting_service.update_attendance("M001", "SV02", "Absent")

for u, s in meeting.attendance.items():
    print(u, ":", s)

print("\n=== UPDATE NOTES ===")
meeting_service.update_notes("M001", "Discussed tasks and deadlines.")
print("Notes:", meeting.notes)

# ===== WHITEBOARD =====
from services.whiteboard_service import WhiteboardService

whiteboard_service = WhiteboardService()

print("\n=== GET WHITEBOARD STATE ===")
wb = whiteboard_service.get_whiteboard_state("P001")
print("Project:", wb.project_id)
print("State:", wb.state)

print("\n=== SAVE WHITEBOARD SNAPSHOT ===")
new_state = {
    "shapes": ["rectangle", "circle", "arrow"],
    "texts": ["Sprint goal", "Done"]
}

updated_wb = whiteboard_service.save_whiteboard_snapshot("P001", new_state)
print("Saved State:", updated_wb.state)
