from flask import Blueprint, request, jsonify, g
from infrastructure.databases.mssql import SessionLocal
from infrastructure.repositories.evaluation_repository import EvaluationRepository
from infrastructure.services.evaluation_service import EvaluationService
from api.middleware import auth_required

# Đổi tên Blueprint thành 'evaluation'
evaluation_bp = Blueprint('evaluation', __name__, url_prefix='/api/v1/evaluation')

def get_service():
    session = SessionLocal()
    repo = EvaluationRepository(session)
    return EvaluationService(repo)

@evaluation_bp.route('/submissions', methods=['POST'])
@auth_required
def submit_assignment():
    """
    Sinh viên nộp bài cho một Checkpoint
    ---
    tags:
      - Evaluation
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            checkpoint_id: {type: integer}
            file_url: {type: string}
    responses:
      201:
        description: Nộp bài thành công
    """
    service = get_service()
    data = request.json
    try:
        sub = service.submit_assignment(g.user_id, data)
        return jsonify({
            "message": "Nộp bài thành công",
            "submission_id": sub.id,
            "checkpoint_id": sub.checkpoint_id,
            "status": "Submitted"
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@evaluation_bp.route('/peer-reviews', methods=['POST'])
@auth_required
def peer_review():
    service = get_service()
    data = request.json
    try:
        service.submit_peer_review(g.user_id, data)
        return jsonify({"message": "Đánh giá thành công"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@evaluation_bp.route('/grades', methods=['POST'])
@auth_required
def grade_submission():
    """
    Giảng viên chấm điểm bài nộp
    ---
    tags:
      - Evaluation
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            submission_id: {type: integer}
            score: {type: number}
            feedback: {type: string}
    responses:
      200:
        description: Chấm điểm thành công
    """
    service = get_service()
    data = request.json
    try:
        if g.user_role != 'Lecturer' and g.user_role != 'Admin':
             return jsonify({"error": "Unauthorized"}), 403

        result = service.instructor_grade(
            submission_id=data.get('submission_id'),
            score=data.get('score'),
            feedback=data.get('feedback')
        )
        return jsonify({"message": "Chấm điểm thành công", "score": result.score}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@evaluation_bp.route('/peer-evaluations/my-results', methods=['GET'])
@auth_required
def get_my_peer_results():
    service = get_service()
    try:
        # g.user_id lấy từ token middleware
        results = service.get_my_peer_results(g.user_id)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@evaluation_bp.route('/milestones', methods=['GET'])
@auth_required
def get_all_milestones():
    service = get_service()
    try:
        data = service.get_all_milestones()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@evaluation_bp.route('/grades/student/transcript', methods=['GET'])
@auth_required
def get_transcript():
    service = get_service()
    try:
        data = service.get_student_transcript(g.user_id)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500