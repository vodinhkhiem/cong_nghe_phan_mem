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
    assert "reply" in data
    assert data["conversation_id"] == "test_conv_1"


def test_task_breakdown():
    payload = {
        "task_description": "Thiết kế API backend cho hệ thống học tập"
    }

    response = client.post("/ai/tasks/1/breakdown", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "suggested_checklist" in data
    assert len(data["suggested_checklist"]) > 0


def test_code_explain():
    payload = {
        "code_snippet": "print(x)",
        "error_log": "NameError: name 'x' is not defined"
    }

    response = client.post("/ai/code/explain", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "analysis" in data
    assert "possible_reason" in data["analysis"]


def test_resource_recommend():
    payload = {
        "topic": "AI"   # ✅ topic có thật
    }

    response = client.post("/ai/resources/recommend", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "resources" in data
    assert len(data["resources"]) > 0
    assert "AI" in data["resources"][0]["title"]
