from flask import Blueprint, request, jsonify, g
from infrastructure.databases.mssql import SessionLocal
from infrastructure.repositories.ai_repository import AIRepository
from infrastructure.services.ai_service import AIService
from api.middleware import auth_required

ai_bp = Blueprint('ai', __name__, url_prefix='/api/v1/ai')

def get_service():
    session = SessionLocal()
    repo = AIRepository(session)
    return AIService(repo)

# 1. Chat thông thường
@ai_bp.route('/chat', methods=['POST'])
@auth_required
def chat():
    service = get_service()
    data = request.json
    try:
        result = service.chat_general(g.user_id, data)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 2. Chia nhỏ Task
@ai_bp.route('/tasks/<int:task_id>/breakdown', methods=['POST'])
@auth_required
def breakdown_task(task_id):
    """
    AI gợi ý chia nhỏ Task lớn thành Checklist
    ---
    tags:
      - AI Support
    security:
      - Bearer: []
    parameters:
      - name: task_id
        in: path
        type: integer
    responses:
      200:
        description: Trả về danh sách checklist items gợi ý
    """
    service = get_service()
    data = request.json or {} 
    try:
        result = service.breakdown_task(task_id, data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 3. Giải thích Code
@ai_bp.route('/code/explain', methods=['POST'])
@auth_required
def explain_code():
    service = get_service()
    data = request.json
    try:
        result = service.explain_code(data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 4. Gợi ý tài liệu
@ai_bp.route('/resources/recommend', methods=['POST'])
@auth_required
def recommend_resources():
    service = get_service()
    data = request.json
    try:
        result = service.recommend_resources(data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 5. Lịch sử Chat
@ai_bp.route('/history', methods=['GET'])
@auth_required
def get_history():
    service = get_service()
    try:
        data = service.get_history(g.user_id)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500