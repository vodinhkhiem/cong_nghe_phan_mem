from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_dashboard_student():
    response = client.get("/dashboard/student")
    assert response.status_code == 200

    data = response.json()
    assert "deadlines_sap_toi" in data
    assert "task_dang_lam" in data
    assert "thong_bao_moi" in data
    assert isinstance(data["deadlines_sap_toi"], list)


def test_dashboard_lecturer():
    response = client.get("/dashboard/lecturer")
    assert response.status_code == 200

    data = response.json()
    assert "so_bai_can_cham" in data
    assert "nhom_cham_tien_do" in data
    assert isinstance(data["nhom_cham_tien_do"], list)


def test_clo_attainment():
    response = client.get("/analytics/clo-attainment")
    assert response.status_code == 200

    data = response.json()
    assert "mon_hoc" in data
    assert "clo_attainment" in data
    assert len(data["clo_attainment"]) > 0
