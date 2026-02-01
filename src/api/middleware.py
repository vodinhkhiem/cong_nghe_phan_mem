from flask import request, jsonify, g
from functools import wraps
import jwt
from infrastructure.databases.mssql import SessionLocal
from infrastructure.repositories.user_repository import UserRepository
from api.constants import SECRET_KEY, ALGORITHM

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 1. Lấy token từ Header "Authorization: Bearer <token>"
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]
        
        # --- CƠ CHẾ FALLBACK CHO TEST TEAM ---
        if not token:
            user_id = request.headers.get('X-User-ID')
            if user_id:
                g.user_id = int(user_id)
                g.user_role = request.headers.get('X-User-Role', 'Student')
                return f(*args, **kwargs)
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            # 2. Giải mã Token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # 3. Kiểm tra Blacklist
            session = SessionLocal()
            try:
                repo = UserRepository(session)
                jti = payload.get('jti')
                if jti and repo.is_token_blocked(jti):
                    return jsonify({'message': 'Token has been revoked!'}), 401
            finally:
                session.close()

            # 4. Lưu vào g (Ép kiểu int cho ID)
            g.user_id = int(payload['sub'])
            g.user_role = payload.get('role', 'Student')
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except Exception as e:
            return jsonify({'message': f'Invalid token: {str(e)}'}), 401

        return f(*args, **kwargs)
    return decorated

def setup_middlewares(app):
    @app.errorhandler(Exception)
    def handle_exception(error):
        # Đã sửa thụt lề chuẩn 4 dấu cách
        print(f"❌ [SERVER ERROR]: {str(error)}") 
        response = jsonify({'error': str(error)})
        response.status_code = 500
        if isinstance(error, PermissionError): response.status_code = 403
        return response