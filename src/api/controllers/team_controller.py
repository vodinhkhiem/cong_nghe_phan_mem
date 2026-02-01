from flask import Blueprint, request, jsonify, g
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import engine
from infrastructure.services.team_service import TeamService
from api.middleware import auth_required

team_bp = Blueprint('team', __name__, url_prefix='/api/v1')

def get_db():
    return Session(bind=engine)

# TOPIC APIS
@team_bp.route('/topics/propose', methods=['POST'])
@auth_required
def propose_topic():
    db = get_db()
    try:
        service = TeamService(db)
        data = request.json
        # TODO: Get Lecturer ID from Token
        lecturer_id = g.user_id
        
        topic = service.propose_topic(data, lecturer_id)
        return jsonify({"message": "Đề xuất thành công", "id": topic.id}), 201
    finally:
        db.close()

@team_bp.route('/topics/<int:topic_id>/approval', methods=['PUT'])
def approve_topic(topic_id):
    db = get_db()
    try:
        service = TeamService(db)
        status = request.json.get('status') # 'APPROVED'
        
        service.approve_topic(topic_id, status)
        return jsonify({"message": "Đã cập nhật trạng thái đề tài"}), 200
    finally:
        db.close()

@team_bp.route('/topics/available', methods=['GET'])
def get_available_topics():
    db = get_db()
    try:
        service = TeamService(db)
        topics = service.get_available_topics()
        return jsonify({"data": [{"id": t.id, "name": t.name, "slots": f"{t.current_slots}/{t.max_slots}"} for t in topics]}), 200
    finally:
        db.close()

# TEAM & REQUEST APIS
@team_bp.route('/teams', methods=['POST'])
@auth_required
def create_team():
    """
    Sinh viên tạo nhóm mới
    ---
    tags:
      - Team
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            name: {type: string}
            class_id: {type: integer}
    responses:
      201:
        description: Tạo nhóm thành công
    """
    db = get_db()
    try:
        service = TeamService(db)
        data = request.json
        # Lấy user_id từ header để đồng bộ với test
        user_id = g.user_id
        
        team = service.create_team(data, int(user_id))
        return jsonify({"message": "Tạo nhóm thành công", "id": team.id}), 201
    finally:
        db.close()

@team_bp.route('/teams/<int:team_id>/join-request', methods=['POST'])
@auth_required
def request_join(team_id):
    """SV xin vào nhóm"""
    db = get_db()
    try:
        service = TeamService(db)
        user_id = g.user_id
        
        service.request_join_team(team_id, user_id)
        return jsonify({"message": "Đã gửi yêu cầu tham gia"}), 201
    finally:
        db.close()

@team_bp.route('/teams/requests/<int:req_id>/approve', methods=['PUT'])
@auth_required
def approve_request(req_id):
    """Leader duyệt thành viên"""
    db = get_db()
    try:
        service = TeamService(db)
        leader_id = g.user_id
        
        service.process_join_request(req_id, 'approve', leader_id)
        return jsonify({"message": "Đã duyệt thành viên vào nhóm"}), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    finally:
        db.close()

@team_bp.route('/teams/requests/<int:req_id>/reject', methods=['PUT'])
@auth_required
def reject_request(req_id):
    db = get_db()
    try:
        service = TeamService(db)
        leader_id = g.user_id
        service.process_join_request(req_id, 'reject', leader_id)
        return jsonify({"message": "Đã từ chối yêu cầu"}), 200
    finally:
        db.close()

@team_bp.route('/teams/<int:team_id>/leave', methods=['DELETE'])
@auth_required
def leave_team(team_id):
    db = get_db()
    try:
        service = TeamService(db)
        user_id = g.user_id
        
        service.leave_team(team_id, user_id)
        return jsonify({"message": "Đã rời nhóm"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@team_bp.route('/teams/<int:team_id>/register-topic', methods=['POST'])
@auth_required
def register_topic(team_id):
    """Đăng ký đề tài"""
    """
    Nhóm trưởng chốt đề tài
    ---
    tags:
      - Team
    security:
      - Bearer: []
    parameters:
      - name: team_id
        in: path
        type: integer
      - in: body
        name: body
        schema:
          type: object
          properties:
            topic_id: {type: integer}
    responses:
      200:
        description: Đăng ký đề tài thành công
    """
    db = get_db()
    try:
        service = TeamService(db)
        user_id = g.user_id 
        topic_id = request.json.get('topic_id')
        
        service.register_topic(team_id, topic_id, user_id)
        return jsonify({"message": "Đăng ký đề tài thành công"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()