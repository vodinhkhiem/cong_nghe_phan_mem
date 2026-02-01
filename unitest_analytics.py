from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

# =========================
# STUDENT DASHBOARD
# =========================
def test_student_dashboard():
    response = client.get("/dashboard/student")

    assert response.status_code == 200
    data = response.json()
    assert "upcoming_deadlines" in data
    assert "doing_tasks" in data
    assert "new_notifications" in data


# =========================
# LECTURER DASHBOARD
# =========================
def test_lecturer_dashboard():
    response = client.get("/dashboard/lecturer")

    assert response.status_code == 200
    data = response.json()
    assert "pending_grading_count" in data
    assert "slow_progress_groups" in data


# =========================
# CLO ATTAINMENT
# =========================
def test_clo_attainment():
    response = client.get("/analytics/clo-attainment")

    assert response.status_code == 200
    data = response.json()
    assert "clo_statistics" in data
    assert "average_attainment" in data
