from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from typing import List

ai_router = APIRouter()

chat_history = []

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

@ai_router.post("/ai/chat")
def ai_chat(request: ChatRequest):
    reply = f"[AI hỗ trợ học tập] {request.message}"

    chat_history.append({
        "conversation_id": request.conversation_id,
        "question": request.message,
        "answer": reply,
        "time": datetime.now().isoformat()
    })

    return {
        "status": "success",
        "reply": reply
    }

@ai_router.post("/ai/tasks/{task_id}/breakdown")
def breakdown_task(task_id: int, request: TaskBreakdownRequest):
    checklist = [
        "Phân tích yêu cầu bài toán",
        "Xác định chức năng chính",
        "Thiết kế Use Case / Class Diagram",
        "Cài đặt từng module",
        "Kiểm thử và hoàn thiện"
    ]

    return {
        "status": "success",
        "task_id": task_id,
        "task_description": request.task_description,
        "suggested_checklist": checklist
    }

@ai_router.post("/ai/code/explain")
def explain_code(request: CodeExplainRequest):
    return {
        "status": "success",
        "analysis": {
            "error_log": request.error_log,
            "possible_reason": "Lỗi cú pháp hoặc thiếu import",
            "suggestion": "Kiểm tra lại khai báo biến, hàm hoặc thư viện"
        }
    }

@ai_router.post("/ai/resources/recommend")
def recommend_resources(request: ResourceRequest):
    resources = {
        "CNPM": [
            {"title": "Software Engineering - GeeksforGeeks", "link": "https://www.geeksforgeeks.org/software-engineering/"},
            {"title": "SDLC Overview", "link": "https://www.tutorialspoint.com/sdlc"}
        ],
        "AI": [
            {"title": "IBM - What is AI", "link": "https://www.ibm.com/topics/artificial-intelligence"}
        ]
    }

    return {
        "status": "success",
        "topic": request.topic,
        "resources": resources.get(request.topic, [])
    }

@ai_router.get("/ai/history")
def get_chat_history():
    return {
        "status": "success",
        "history": chat_history
    }
