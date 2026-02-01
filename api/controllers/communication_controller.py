from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import engine
from infrastructure.services.communication_service import CommunicationService

comm_bp = Blueprint('communication', __name__, url_prefix='/api/v1')

def get_db():
    return Session(bind=engine)

# 1. CHAT API
@comm_bp.route('/chat/conversations', methods=['GET'])
def get_conversations():
    """
    Lấy danh sách hội thoại (Các nhóm mà user tham gia).
    Giả định: User ID lấy từ Token (Mock = 1 hoặc query param user_id).
    """
    user_id = request.args.get('user_id', type=int) # TODO: Lấy từ JWT Token
    if not user_id:
        return jsonify({"status": "error", "message": "Missing user_id"}), 400
        
    db = get_db()
    try:
        teams = CommunicationService.get_user_conversations(db, user_id)
        result = [{
            "id": t.id,
            "name": t.name,
            "type": "TEAM"
        } for t in teams]
        return jsonify({"status": "success", "data": result}), 200
    finally:
        db.close()

@comm_bp.route('/chat/conversations/<int:team_id>/messages', methods=['GET'])
def get_messages(team_id):
    """Lấy tin nhắn của một nhóm."""
    db = get_db()
    try:
        msgs = CommunicationService.get_messages(db, team_id)
        result = [{
            "id": m.id,
            "sender_id": m.sender_id,
            "sender_name": m.sender.full_name if m.sender else "Unknown",
            "content": m.content,
            "created_at": m.created_at
        } for m in msgs]
        return jsonify({"status": "success", "data": result}), 200
    finally:
        db.close()

@comm_bp.route('/chat/conversations/<int:team_id>/messages', methods=['POST'])
def send_message(team_id):
    """
    Gửi tin nhắn vào nhóm chat
    ---
    tags:
      - Communication
    parameters:
      - name: team_id
        in: path
        type: integer
      - in: body
        name: body
        schema:
          type: object
          properties:
            content: {type: string}
            sender_id: {type: integer}
    responses:
      201:
        description: Gửi tin nhắn thành công
    """
    db = get_db()
    try:
        body = request.json
        sender_id = body.get('sender_id') # TODO: Lấy từ JWT
        content = body.get('content')
        
        if not content:
            return jsonify({"status": "error", "message": "Content is required"}), 400

        msg = CommunicationService.send_message(db, team_id, sender_id, content)
        return jsonify({"status": "success", "data": {"id": msg.id, "created_at": msg.created_at}}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close()

# 2. MEETING API
@comm_bp.route('/meetings', methods=['POST'])
def create_meeting():
    """
    Tạo lịch họp nhóm (Meeting)
    ---
    tags:
      - Communication
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            team_id: {type: integer}
            title: {type: string}
            start_time: {type: string, format: date-time}
            location: {type: string}
            is_online: {type: boolean}
    responses:
      201:
        description: Tạo lịch họp thành công
    """
    db = get_db()
    try:
        body = request.json
        creator_id = body.get('creator_id') # TODO: Lấy từ JWT
        
        # Validate data cơ bản
        if not body.get('team_id') or not body.get('start_time'):
             return jsonify({"status": "error", "message": "Missing required fields"}), 400

        meeting = CommunicationService.create_meeting(db, body, creator_id)
        return jsonify({"status": "success", "message": "Meeting created", "id": meeting.id}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close()

@comm_bp.route('/teams/<int:team_id>/meetings', methods=['GET'])
def get_meetings(team_id):
    """Lấy danh sách cuộc họp của nhóm."""
    db = get_db()
    try:
        meetings = CommunicationService.get_team_meetings(db, team_id)
        result = [{
            "id": m.id,
            "title": m.title,
            "start_time": m.start_time,
            "location": m.location,
            "is_online": m.is_online
        } for m in meetings]
        return jsonify({"status": "success", "data": result}), 200
    finally:
        db.close()

@comm_bp.route('/meetings/<int:meeting_id>/attendance', methods=['PUT'])
def mark_attendance(meeting_id):
    """SV điểm danh (Có mặt / Vắng)."""
    db = get_db()
    try:
        body = request.json
        user_id = body.get('user_id') # TODO: Lấy từ JWT
        status = body.get('status') # 'Present', 'Absent'
        
        if status not in ['Present', 'Absent']:
            return jsonify({"status": "error", "message": "Invalid status"}), 400

        success = CommunicationService.mark_attendance(db, meeting_id, user_id, status)
        if success:
            return jsonify({"status": "success", "message": "Attendance marked"}), 200
        else:
            return jsonify({"status": "error", "message": "User not in meeting list"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close()

@comm_bp.route('/meetings/<int:meeting_id>/notes', methods=['PUT'])
def update_notes(meeting_id):
    """Thư ký lưu biên bản họp."""
    db = get_db()
    try:
        body = request.json
        notes = body.get('notes')
        
        success = CommunicationService.update_notes(db, meeting_id, notes)
        if success:
            return jsonify({"status": "success", "message": "Notes updated"}), 200
        return jsonify({"status": "error", "message": "Meeting not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close()