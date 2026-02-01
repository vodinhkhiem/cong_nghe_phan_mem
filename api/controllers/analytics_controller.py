from flask import Blueprint, request, jsonify, g
from infrastructure.databases.mssql import SessionLocal
from infrastructure.repositories.analytics_repository import AnalyticsRepository
from infrastructure.services.analytics_service import AnalyticsService
from api.middleware import auth_required

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/v1')

def get_service():
    session = SessionLocal()
    repo = AnalyticsRepository(session)
    return AnalyticsService(repo)

# 1. Dashboard Sinh viên
@analytics_bp.route('/dashboard/student', methods=['GET'])
@auth_required
def get_student_dashboard():
    """
    Aggregation API: Deadlines sắp tới, Task đang làm.
    """
    """
    Dashboard Sinh viên: Xem deadline và Task đang làm
    ---
    tags:
      - Analytics
    security:
      - Bearer: []
    responses:
      200:
        description: JSON chứa danh sách upcoming_deadlines và active_tasks
    """
    service = get_service()
    try:
        data = service.get_student_dashboard(g.user_id)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 2. Dashboard Giảng viên
@analytics_bp.route('/dashboard/lecturer', methods=['GET'])
@auth_required
def get_lecturer_dashboard():
    """
    Aggregation API: Số bài cần chấm, Các nhóm chậm tiến độ.
    """
    """
    Dashboard Giảng viên: Xem bài cần chấm và nhóm chậm tiến độ
    ---
    tags:
      - Analytics
    security:
      - Bearer: []
    responses:
      200:
        description: JSON chứa pending_grading_count và lagging_teams
    """
    service = get_service()
    try:
        if g.user_role not in ['Lecturer', 'Admin', 'HeadOfDept']:
            return jsonify({"error": "Forbidden"}), 403
            
        data = service.get_lecturer_dashboard(g.user_id)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 3. Thống kê CLO 
@analytics_bp.route('/analytics/clo-attainment', methods=['GET'])
@auth_required
def get_clo_attainment():
    """
    Thống kê mức độ đạt chuẩn đầu ra.
    """
    service = get_service()
    try:
        if g.user_role not in ['Admin', 'HeadOfDept', 'Lecturer']:
             return jsonify({"error": "Forbidden"}), 403

        data = service.get_clo_attainment()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500