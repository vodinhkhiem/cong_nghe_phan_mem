from flask import Blueprint, request, jsonify
from services.team_service import TeamService
from api.middleware import middleware 

# Khởi tạo Blueprint cho module Team
team_bp = Blueprint('team_bp', __name__)
team_service = TeamService()

@team_bp.route('/teams', methods=['POST'])
# [TODO]: Uncomment dòng dưới để bật xác thực Token khi chạy thật
# @middleware
def create_team():
    """
    API Tạo nhóm mới.
    ---
    tags:
      - Team Management
    parameters:
      - in: body
        name: body
        schema:
          properties:
            name:
              type: string
            class_id:
              type: string
    """
    try:
        # [LOGIC]: Authentication Placeholder
        # TODO: Cần thay thế bằng code lấy ID từ JWT Token (VD: request.user.id)
        current_user_id = 1 
        
        # Nhận dữ liệu JSON từ Client
        data = request.json
        
        # Gọi Service xử lý logic
        team = team_service.create_team(data, current_user_id)
        
        # Trả về Response chuẩn RESTful (201 Created)
        return jsonify({"message": "Tạo nhóm thành công", "id": team.id}), 201
    except Exception as e:
        # Xử lý lỗi chung (Global Exception Handling)
        return jsonify({"error": str(e)}), 400

@team_bp.route('/teams/<int:team_id>/register-topic', methods=['POST'])
def register_topic(team_id):
    """
    API Đăng ký đề tài (Chỉ Leader mới dùng được).
    """
    try:
        current_user_id = 1 # TODO: Lấy từ token thật
        data = request.json
        
        # Service sẽ ném lỗi PermissionError nếu không phải Leader
        team_service.register_topic(team_id, data, current_user_id)
        
        return jsonify({"message": "Đăng ký đề tài thành công"}), 200
    except PermissionError as e:
        # Trả về mã 403 Forbidden nếu không có quyền
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 400