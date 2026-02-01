from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_ai_chat():
    response = client.post(
        "/ai/chat",
        json={
            "message": "Use Case là gì?",
            "conversation_id": "test01"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "context_used" in data

def test_task_breakdown():
    response = client.post(
        "/ai/tasks/1/breakdown",
        json={
            "task_description": "Làm đồ án quản lý tài nguyên"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == 1
    assert len(data["suggested_checklist"]) > 0

def test_code_explain():
    response = client.post(
        "/ai/code/explain",
        json={
            "code_snippet": "print(x)",
            "error_log": "NameError: name 'x' is not defined"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "ai_analysis" in data


def test_resource_recommend():
    response = client.post(
        "/ai/resources/recommend",
        json={
            "topic": "CNPM"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "recommended_resources" in data


def test_chat_history():
    response = client.get("/ai/history")

    assert response.status_code == 200
    data = response.json()
    assert "history" in data
