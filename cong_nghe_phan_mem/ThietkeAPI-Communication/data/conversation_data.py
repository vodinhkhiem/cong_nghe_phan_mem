# data/conversation_data.py
# Lưu trữ dữ liệu hội thoại (giả lập DB)

from models.conversation import Conversation
from models.message import Message

class ConversationData:
    def __init__(self):
        self.conversations = []

        # Khởi tạo dữ liệu mẫu
        convo = Conversation("C001", ["user1", "user2"])
        convo.messages.append(Message("user1", "Hello", "10:00"))
        convo.messages.append(Message("user2", "Hi there", "10:01"))

        self.conversations.append(convo)

    # Linear Search – O(n)
    def get_all(self):
        return self.conversations

    def find_by_id(self, convo_id):
        for c in self.conversations:
            if c.conversation_id == convo_id:
                return c
        return None
