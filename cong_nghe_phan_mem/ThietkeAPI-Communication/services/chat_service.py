# services/chat_service.py
# Xử lý API Chat

from data.conversation_data import ConversationData
from models.message import Message

class ChatService:
    def __init__(self):
        self.data = ConversationData()

    # GET /chat/conversations
    def get_conversations(self):
        return self.data.get_all()

    # GET /chat/conversations/{id}/messages
    def get_messages(self, convo_id):
        convo = self.data.find_by_id(convo_id)
        return convo.messages if convo else []

    # POST /chat/conversations/{id}/messages
    def send_message(self, convo_id, sender, content):
        convo = self.data.find_by_id(convo_id)
        if not convo:
            return None

        message = Message(sender, content, "10:05")
        convo.messages.append(message)
        return message
