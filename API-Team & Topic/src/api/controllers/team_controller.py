from flask import Blueprint, request, jsonify
from services.team_service import TeamService

team_bp = Blueprint('team_bp', __name__)
team_service = TeamService()

# TEAM MANAGEMENT 
@team_bp.route('/teams', methods=['POST'])
def create_team():
    try:
        # TODO: Lấy user_id từ Token (VD: request.user_id)
        current_user_id = 1 
        data = request.json
        team = team_service.create_team(data, current_user_id)
        return jsonify({"message": "Tạo nhóm thành công", "id": team.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@team_bp.route('/teams/<int:team_id>/leave', methods=['DELETE'])
def leave_team(team_id):
    """API: Rời nhóm"""
    try:
        current_user_id = 1 # TODO: Token
        team_service.leave_team(team_id, current_user_id)
        return jsonify({"message": "Đã rời nhóm thành công"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# TOPIC MANAGEMENT 
@team_bp.route('/topics', methods=['POST'])
def create_topic():
    """API: Tạo đề tài (GV hoặc SV)"""
    try:
        current_user_id = 1 # TODO: Token
        # TODO: Lấy role từ Token ('Lecturer' hoặc 'Student')
        current_role = request.json.get('role_mock', 'Student') 
        
        data = request.json
        topic = team_service.create_topic(data, current_user_id, current_role)
        return jsonify({"message": "Tạo đề tài thành công", "status": topic.status}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@team_bp.route('/topics', methods=['GET'])
def get_list_topics():
    """API: Lấy danh sách đề tài"""
    topics = team_service.get_topics()
    result = [{
        "id": t.id, 
        "title": t.title, 
        "status": t.status, 
        "is_gv_suggested": t.is_suggested_by_gv
    } for t in topics]
    return jsonify(result), 200

@team_bp.route('/topics/<int:topic_id>/approve', methods=['PUT'])
def approve_topic(topic_id):
    """API: GV duyệt đề tài"""
    try:
        current_role = 'Lecturer' # TODO: Token
        team_service.approve_topic(topic_id, current_role)
        return jsonify({"message": "Đã duyệt đề tài"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@team_bp.route('/teams/<int:team_id>/register-topic', methods=['POST'])
def register_topic(team_id):
    """API: Leader đăng ký đề tài cho nhóm"""
    try:
        current_user_id = 1 # TODO: Token
        data = request.json
        team_service.register_topic_for_team(team_id, data, current_user_id)
        return jsonify({"message": "Đăng ký đề tài thành công"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# MEMBERSHIP REQUESTS
@team_bp.route('/teams/<int:team_id>/join', methods=['POST'])
def join_team(team_id):
    """API: SV xin vào nhóm"""
    try:
        current_user_id = 2 # TODO: Token (Người xin)
        team_service.request_to_join(team_id, current_user_id)
        return jsonify({"message": "Đã gửi yêu cầu xin vào nhóm"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@team_bp.route('/teams/<int:team_id>/invite', methods=['POST'])
def invite_member(team_id):
    """API: Leader mời SV"""
    try:
        current_user_id = 1 # TODO: Token (Leader)
        target_user_id = request.json.get('user_id')
        team_service.invite_member(team_id, target_user_id, current_user_id)
        return jsonify({"message": "Đã gửi lời mời"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@team_bp.route('/requests/<int:request_id>/respond', methods=['PUT'])
def respond_request(request_id):
    """
    API: Duyệt/Từ chối Request.
    Body: { "action": "approve" } hoặc { "action": "reject" }
    """
    try:
        current_user_id = 1 # TODO: Token (Người đang thao tác duyệt)
        action = request.json.get('action')
        team_service.respond_to_request(request_id, action, current_user_id)
        return jsonify({"message": f"Đã {action} yêu cầu thành công"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400