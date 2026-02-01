from services.chat_service import ChatService
from services.meeting_service import MeetingService
from services.whiteboard_service import WhiteboardService

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


# ===== WHITEBOARD =====
whiteboard_service = WhiteboardService()

# ===== MEETING =====
meeting_service = MeetingService(whiteboard_service)

print("\n=== CREATE MEETING ===")
meeting_service.create_meeting(
    "M001",
    "Sprint Planning",
    "Google Meet"
)

print("\n=== JOIN MEETING WITH WHITEBOARD ===")
join_info = meeting_service.join_meeting("M001", use_whiteboard=True)
print(join_info)

project_id = join_info["project_id"]

print("\n=== GET WHITEBOARD STATE ===")
print(whiteboard_service.get_state(project_id))

print("\n=== SAVE WHITEBOARD SNAPSHOT ===")
whiteboard_service.save_snapshot(project_id, {
    "shapes": ["circle"],
    "texts": ["Sprint Goal"]
})

print("\n=== GET WHITEBOARD STATE AFTER UPDATE ===")
print(whiteboard_service.get_state(project_id))
