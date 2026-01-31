# models/conversation.py
# Model hội thoại

class Conversation:
    def __init__(self, conversation_id, participants):
        self.conversation_id = conversation_id
        self.participants = participants
        self.messages = []
