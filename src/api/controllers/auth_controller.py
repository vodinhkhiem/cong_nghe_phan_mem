from flask import Blueprint, request, jsonify
from infrastructure.databases.mssql import SessionLocal
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

def get_service():
    session = SessionLocal()
    repo = UserRepository(session)
    return AuthService(repo)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Đăng ký tài khoản mới
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            full_name: {type: string}
            email: {type: string}
            password: {type: string}
            role: {type: string, enum: [Student, Lecturer]}
    responses:
      201:
        description: Đăng ký thành công
    """
    data = request.json
    service = get_service()
    try:
        user = service.register(
            full_name=data.get('full_name'),
            email=data.get('email'),
            password=data.get('password'),
            role=data.get('role', 'Student')
        )
        return jsonify({"message": "Đăng ký thành công", "email": user.email}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # In lỗi ra terminal để debug
        print(f"❌ ERROR DETAILS: {str(e)}") 
        # Trả về lỗi chi tiết cho client/test thấy
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Đăng nhập hệ thống
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            email: {type: string}
            password: {type: string}
    responses:
      200:
        description: Trả về accessToken và role
    """
    data = request.json
    service = get_service()
    try:
        result = service.login(
            email=data.get('email'),
            password=data.get('password')
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        # In lỗi ra terminal để debug
        print(f"❌ ERROR DETAILS: {str(e)}") 
        # Trả về lỗi chi tiết cho client/test thấy
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/refresh-token', methods=['POST'])
def refresh_token():
    data = request.json
    service = get_service()
    try:
        new_token = service.refresh_token(data.get('refreshToken'))
        return jsonify({"accessToken": new_token}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(" ")[1]
        service = get_service()
        service.logout(token)
    return jsonify({"message": "Đăng xuất thành công"}), 200

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    service = get_service()
    service.forgot_password(data.get('email'))
    return jsonify({"message": "Nếu email tồn tại, hướng dẫn đặt lại mật khẩu sẽ được gửi đi."}), 200

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    service = get_service()
    try:
        service.reset_password(data.get('token'), data.get('new_password'))
        return jsonify({"message": "Đặt lại mật khẩu thành công"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400