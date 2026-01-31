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
msg = chat_service.send_message("C001", "user2", "Hi, I received your message")
print("Sent:", msg.content)

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
attendance = meeting_service.update_attendance("M001", "SV01", "Present")
attendance = meeting_service.update_attendance("M001", "SV02", "Absent")
for sv, st in attendance.items():
    print(sv, ":", st)

print("\n=== UPDATE NOTES ===")
notes = meeting_service.update_notes(
    "M001",
    "Discussed tasks and deadlines."
)
print("Notes:", notes)

from services.whiteboard_service import WhiteboardService
whiteboard_service = WhiteboardService()


print("\n=== JOIN MEETING WITH WHITEBOARD ===")
join_response = meeting_service.join_meeting("M001", use_whiteboard=True)
print(join_response)

if join_response["has_whiteboard"]:
    print("\n=== GET WHITEBOARD STATE ===")
    state = whiteboard_service.get_state(join_response["whiteboard_id"])
    print("State:", state)

    print("\n=== SAVE WHITEBOARD SNAPSHOT ===")
    new_state = {
        "shapes": ["circle", "rectangle"],
        "texts": ["Sprint goals"]
    }
    whiteboard_service.save_snapshot(join_response["whiteboard_id"], new_state)

    print("\n=== GET WHITEBOARD STATE AFTER UPDATE ===")
    state = whiteboard_service.get_state(join_response["whiteboard_id"])
    print("State:", state)

