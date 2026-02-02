from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_ai_chat():
    payload = {
        "message": "CLO là gì?",
        "conversation_id": "test_conv_1"
    }

    response = client.post("/ai/chat", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "answer" in data
    assert data["conversation_id"] == "test_conv_1"


def test_task_breakdown():
    payload = {
        "task_description": "Thiết kế hệ thống Learning Analytics"
    }

    response = client.post("/ai/tasks/1/breakdown", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "checklist_items" in data
    assert isinstance(data["checklist_items"], list)


def test_code_explain():
    payload = {
        "code_snippet": "print(x)",
        "error_log": "NameError: name 'x' is not defined"
    }

    response = client.post("/ai/code/explain", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "explanation" in data


def test_resource_recommend():
    payload = {
        "topic": "FastAPI"
    }

    response = client.post("/ai/resources/recommend", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "resources" in data
    assert isinstance(data["resources"], list)


def test_chat_history():
    response = client.get("/ai/history")
    assert response.status_code == 200

    data = response.json()
    assert "history" in data
