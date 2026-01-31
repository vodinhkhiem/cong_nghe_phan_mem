# File: analytics_get.py
from flask import Blueprint, jsonify

analytics_bp = Blueprint("analytics_bp", __name__)

# --- 1. Dashboard Sinh Viên ---
# Yêu cầu: Aggregation API (Deadlines sắp tới, Task đang làm, Thông báo mới)
@analytics_bp.route("/dashboard/student", methods=["GET"])
def get_student_dashboard():
    # Giả lập việc query 3 bảng khác nhau trong Database rồi gộp lại
    data = {
        "deadlines_sap_toi": [
            {"id": 1, "môn": "Lập trình Web", "tiêu_đề": "Nộp Assignment 1", "hạn": "2024-05-20", "trạng_thái": "Gấp"},
            {"id": 2, "môn": "CSDL", "tiêu_đề": "Quiz Online Lab 3", "hạn": "2024-05-22", "trạng_thái": "Bình thường"}
        ],
        "tasks_dang_lam": [
            {"id": 101, "tên_task": "Thiết kế Figma", "tiến_độ": 50},
            {"id": 102, "tên_task": "Viết API Backend", "tiến_độ": 30}
        ],
        "thong_bao_moi": [
            {"nguồn": "Phòng Đào Tạo", "nội_dung": "Lịch nghỉ lễ 30/4 - 1/5", "ngày": "2024-04-15"},
            {"nguồn": "GVCN", "nội_dung": "Nhắc nhở đóng học phí kỳ Spring", "ngày": "2024-04-10"}
        ]
    }
    return jsonify({"status": "success", "data": data})

# --- 2. Dashboard Giảng Viên ---
# Yêu cầu: Số bài cần chấm, Các nhóm chậm tiến độ
@analytics_bp.route("/dashboard/lecturer", methods=["GET"])
def get_lecturer_dashboard():
    data = {
        "thong_ke_can_cham": {
            "tong_so": 15,
            "chi_tiet": "5 bài Lab, 10 bài Assignment"
        },
        "nhom_cham_tien_do": [
            {"nhom": "Group 01", "du_an": "Web Bán Hàng", "tre_han": "3 ngày"},
            {"nhom": "Group 05", "du_an": "App Điểm Danh", "tre_han": "5 ngày"}
        ]
    }
    return jsonify({"status": "success", "data": data})

# --- 3. Analytics Trưởng Bộ Môn ---
# Yêu cầu: Thống kê mức độ đạt chuẩn đầu ra (CLO)
@analytics_bp.route("/analytics/clo-attainment", methods=["GET"])
def get_clo_stats():
    data = {
        "mon_hoc": "IT101 - Nhập môn Lập trình",
        "thong_ke_clo": [
            {"clo_code": "CLO1", "mo_ta": "Tư duy logic", "dat_chuan": "85%"},
            {"clo_code": "CLO2", "mo_ta": "Kỹ năng Code", "dat_chuan": "70%"},
            {"clo_code": "CLO3", "mo_ta": "Làm việc nhóm", "dat_chuan": "92%"}
        ]
    }
    return jsonify({"status": "success", "data": data})