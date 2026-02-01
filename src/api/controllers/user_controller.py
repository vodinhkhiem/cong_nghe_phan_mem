from flask import Blueprint, request, jsonify, g
from infrastructure.databases.mssql import SessionLocal
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.services.user_service import UserService
from api.middleware import auth_required

user_bp = Blueprint('user', __name__, url_prefix='/api/v1/users')

def get_service():
    session = SessionLocal()
    repo = UserRepository(session)
    return UserService(repo)

@user_bp.route('/profile', methods=['GET'])
@auth_required
def get_profile():
    """
    Lấy thông tin cá nhân của người dùng hiện tại
    ---
    tags:
      - User
    security:
      - Bearer: []
    responses:
      200:
        description: Trả về chi tiết profile (email, role, avatar...)
    """
    service = get_service()
    try:
        user = service.get_profile(g.user_id)
        return jsonify({
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "avatar_url": user.avatar_url,
            "description": user.description
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@user_bp.route('/profile', methods=['PUT'])
@auth_required
def update_profile():
    service = get_service()
    data = request.json
    try:
        user = service.update_profile(g.user_id, data)
        return jsonify({"message": "Cập nhật thành công"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400