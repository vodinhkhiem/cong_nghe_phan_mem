from flask import Blueprint, request, jsonify, g
from infrastructure.databases.mssql import SessionLocal
from infrastructure.repositories.academic_repository import AcademicRepository
from infrastructure.services.academic_service import AcademicService
from api.middleware import auth_required

academic_bp = Blueprint('academic', __name__, url_prefix='/api/v1')

def get_service():
    session = SessionLocal()
    repo = AcademicRepository(session)
    return AcademicService(repo)

# [GET] /semesters/current
@academic_bp.route('/semesters/current', methods=['GET'])
def get_current_semester():
    """
    Lấy thông tin học kỳ hiện tại
    ---
    tags:
      - Academic
    responses:
      200:
        description: Trả về học kỳ đang diễn ra
    """
    service = get_service()
    try:
        data = service.get_current_semester()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# [PUT] /syllabus/{classId}
@academic_bp.route('/syllabus/<int:class_id>', methods=['PUT'])
@auth_required
def update_syllabus(class_id):
    """
    Giảng viên cập nhật Syllabus cho lớp học
    ---
    tags:
      - Academic
    security:
      - Bearer: []
    parameters:
      - name: class_id
        in: path
        type: integer
      - in: body
        name: body
        schema:
          type: object
          properties:
            content: {type: string}
    responses:
      200:
        description: Cập nhật thành công
    """
    service = get_service()
    data = request.json
    try:
        # Check Role: Chỉ Lecturer/Admin được sửa
        if g.user_role not in ['Lecturer', 'Admin']:
            return jsonify({"error": "Forbidden"}), 403

        result = service.update_syllabus_for_class(class_id, data)
        return jsonify({"message": "Cập nhật Syllabus thành công", "id": result.id}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# [POST] /rubrics
@academic_bp.route('/rubrics', methods=['POST'])
@auth_required
def create_rubric():
    service = get_service()
    data = request.json
    try:
        if g.user_role not in ['Lecturer', 'Admin']:
            return jsonify({"error": "Forbidden"}), 403

        rubric = service.create_rubric(g.user_id, data)
        return jsonify({"message": "Tạo Rubric thành công", "id": rubric.id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

# [GET] /rubrics
@academic_bp.route('/rubrics', methods=['GET'])
@auth_required
def get_rubrics():
    service = get_service()
    try:
        data = service.get_rubrics()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500