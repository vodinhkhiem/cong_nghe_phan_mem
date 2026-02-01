from infrastructure.repositories.ai_repository import AIRepository
from infrastructure.services.ai_llm_client import AILLMClient
import uuid
import json

class AIService:
    def __init__(self, repo: AIRepository):
        self.repo = repo

    def chat_general(self, user_id, data):
        """
        Xử lý chat thông thường[cite: 16].
        """
        message = data.get('message')
        conversation_id = data.get('conversation_id') or str(uuid.uuid4())
        
        if not message:
            raise ValueError("Message không được để trống")

        # 1. Lưu tin nhắn User
        self.repo.save_chat_log(user_id, 'user', message, conversation_id)

        # 2. Gọi AI 
        system_context = "Bạn là trợ lý ảo hỗ trợ môn học Phát triển phần mềm (SWP391)."
        ai_response_text = AILLMClient.generate_response(message, system_context)

        # 3. Lưu tin nhắn Bot
        self.repo.save_chat_log(user_id, 'bot', ai_response_text, conversation_id)

        return {
            "response": ai_response_text,
            "conversation_id": conversation_id
        }

    def breakdown_task(self, task_id, data):
        """
        Gợi ý chia nhỏ công việc thành Checklist (JSON).
        """
        # 1. Lấy thông tin Task
        task = self.repo.get_task_by_id(task_id)
        task_context = data.get('task_description', '')
        if task:
            task_context = f"{task.title}"
            if hasattr(task, 'description') and task.description:
                task_context += f": {task.description}"
        
        if not task_context:
            raise ValueError("Không tìm thấy thông tin Task để phân tích")

        # 2. Prompt kỹ thuật
        prompt = (
            f"Hãy đóng vai Project Manager. Hãy chia nhỏ công việc sau đây thành các bước thực hiện cụ thể."
            f"\nCông việc: \"{task_context}\""
            f"\n\nYÊU CẦU OUTPUT: Chỉ trả về một JSON Array chứa danh sách các string. Không giải thích gì thêm."
            f"\nVí dụ: [\"Nghiên cứu tài liệu\", \"Thiết kế Database\", \"Viết API\"]"
        )
        
        # 3. Gọi AI
        ai_response = AILLMClient.generate_response(prompt)
        
        # 4. Parse JSON an toàn
        try:
            clean_json = ai_response.replace('```json', '').replace('```', '').strip()
            start_idx = clean_json.find('[')
            end_idx = clean_json.rfind(']') + 1
            
            if start_idx != -1 and end_idx != -1:
                clean_json = clean_json[start_idx:end_idx]
                
            suggestion_list = json.loads(clean_json)
            return {"suggestion": suggestion_list} 
            
        except Exception:
            return {"suggestion": [ai_response]}

    def explain_code(self, data):
        """
        Giải thích code/lỗi[cite: 16].
        """
        code = data.get('code_snippet')
        error = data.get('error_log')
        
        prompt = f"Giải thích đoạn code sau và lỗi này:\nCode: {code}\nError: {error}"
        ai_response = AILLMClient.generate_response(prompt)
        
        return {"explanation": ai_response}

    def recommend_resources(self, data):
        """
        Gợi ý tài liệu[cite: 16].
        """
        topic = data.get('topic')
        prompt = f"Gợi ý 3 tài liệu uy tín để học về chủ đề: {topic}"
        ai_response = AILLMClient.generate_response(prompt)
        
        return {"resources": ai_response}

    def get_history(self, user_id):
        """
        Xem lịch sử chat[cite: 16].
        """
        logs = self.repo.get_history_by_user(user_id)
        return [{
            "id": log.id,
            "sender": log.sender,
            "message": log.message,
            "conversation_id": log.conversation_id,
            "created_at": log.created_at.isoformat() if log.created_at else None
        } for log in logs]