from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict

ai_router = APIRouter(prefix="/ai", tags=["AI"])

class ChatRequest(BaseModel):
    message: str
    conversation_id: str

class TaskBreakdownRequest(BaseModel):
    task_description: str

class CodeExplainRequest(BaseModel):
    code_snippet: str
    error_log: str

class ResourceRequest(BaseModel):
    topic: str


chat_history: List[Dict] = []

@ai_router.post("/chat")
def ai_chat(request: ChatRequest):
    reply = f"[AI hỗ trợ học tập] {request.message}"

    chat_history.append({
        "conversation_id": request.conversation_id,
        "question": request.message,
        "reply": reply
    })

    return {
        "status": "success",
        "reply": reply,
        "conversation_id": request.conversation_id
    }

@ai_router.post("/tasks/{task_id}/breakdown")
def breakdown_task(task_id: int, request: TaskBreakdownRequest):
    task_lower = request.task_description.lower()

    if "api" in task_lower or "backend" in task_lower:
        checklist = [
            "Thiết kế Database",
            "Xây dựng API Endpoint",
            "Viết Unit Test",
            "Kiểm tra bằng Postman"
        ]
    elif "giao diện" in task_lower or "frontend" in task_lower:
        checklist = [
            "Phân tích yêu cầu UI",
            "Thiết kế UI/UX",
            "Code React/Vue",
            "Responsive Mobile"
        ]
    else:
        checklist = [
            "Phân tích yêu cầu",
            "Thực hiện task",
            "Kiểm tra kết quả"
        ]

    return {
        "status": "success",
        "task_id": task_id,
        "task_description": request.task_description,
        "suggested_checklist": checklist
    }

@ai_router.post("/code/explain")
def explain_code(request: CodeExplainRequest):
    return {
        "analysis": {
            "possible_reason": "Biến chưa được khai báo trước khi sử dụng",
            "suggestion": "Hãy kiểm tra lại tên biến và scope"
        }
    }

@ai_router.post("/resources/recommend")
def recommend_resources(request: ResourceRequest):
    data = {
        "AI": [
            {"title": "AI Fundamentals - IBM", "link": "https://www.ibm.com"},
            {"title": "Machine Learning Basics", "link": "https://developers.google.com"}
        ],
        "CNPM": [
            {"title": "Software Engineering - Sommerville", "link": "https://example.com"}
        ]
    }

    return {
        "topic": request.topic,
        "resources": data.get(request.topic, [])
    }

@ai_router.get("/history")
def get_chat_history():
    return {
        "total_conversations": len(chat_history),
        "history": chat_history
    }
