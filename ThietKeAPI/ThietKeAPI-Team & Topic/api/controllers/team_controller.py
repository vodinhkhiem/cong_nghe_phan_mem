from flask import Blueprint, request, jsonify
from services.team_service import TeamService

team_bp = Blueprint('team_bp', __name__)
team_service = TeamService()

@team_bp.route('/teams', methods=['POST'])
def create_team():
    try:
        # TODO: Lấy user_id từ Token (JWT) 
        current_user_id = 1 
        data = request.json
        
        team = team_service.create_team(data, current_user_id)
        return jsonify({"message": "Tạo nhóm thành công", "id": team.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@team_bp.route('/teams/<int:team_id>/register-topic', methods=['POST'])
def register_topic(team_id):
    try:
        current_user_id = 1 
        data = request.json
        team_service.register_topic(team_id, data, current_user_id)
        return jsonify({"message": "Đăng ký đề tài thành công"}), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 400