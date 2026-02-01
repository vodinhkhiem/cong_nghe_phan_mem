from fastapi import APIRouter

router = APIRouter(tags=["Analytics"])

@router.get("/dashboard/student")
def dashboard_student():
    """
    Aggregation API:
    - Deadlines sắp tới
    - Task đang làm
    - Thông báo mới
    """
    return {
        "deadlines_sap_toi": [
            {"mon_hoc": "Công nghệ phần mềm", "han_nop": "2026-02-10"},
            {"mon_hoc": "Trí tuệ nhân tạo", "han_nop": "2026-02-15"}
        ],
        "task_dang_lam": [
            "Thiết kế API Learning Analytics",
            "Viết báo cáo nhóm"
        ],
        "thong_bao_moi": [
            "Có bài tập mới môn CNPM",
            "Lớp AI dời lịch học"
        ]
    }


@router.get("/dashboard/lecturer")
def dashboard_lecturer():
    """
    Aggregation API:
    - Số bài cần chấm
    - Các nhóm chậm tiến độ
    """
    return {
        "so_bai_can_cham": 18,
        "nhom_cham_tien_do": [
            {
                "ten_nhom": "Nhóm 01",
                "du_an": "Website bán hàng",
                "tre_han": "3 ngày"
            },
            {
                "ten_nhom": "Nhóm 05",
                "du_an": "App điểm danh",
                "tre_han": "5 ngày"
            }
        ]
    }


@router.get("/analytics/clo-attainment")
def clo_attainment():
    """
    Thống kê mức độ đạt chuẩn đầu ra (CLO)
    Dành cho Trưởng bộ môn
    """
    return {
        "mon_hoc": "IT101 - Nhập môn lập trình",
        "clo_attainment": [
            {
                "clo": "CLO1",
                "mo_ta": "Tư duy logic",
                "ty_le_dat": 85
            },
            {
                "clo": "CLO2",
                "mo_ta": "Kỹ năng lập trình",
                "ty_le_dat": 78
            },
            {
                "clo": "CLO3",
                "mo_ta": "Làm việc nhóm",
                "ty_le_dat": 90
            }
        ]
    }
