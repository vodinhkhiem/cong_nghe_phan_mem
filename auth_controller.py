from flask import Blueprint, request, jsonify
from infrastructure.models import user_model 
from infrastructure.databases.mssql import SessionLocal 

auth_bp = Blueprint('auth', __name__)

# ---------------------------------------------------------
# 1. API Đăng ký tài khoản người dùng (POST /auth/register)
# ---------------------------------------------------------
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    session = SessionLocal()
    response = None # Khởi tạo biến phản hồi hệ thống

    try:
        # Kiểm tra sự tồn tại của Email trong cơ sở dữ liệu để tránh trùng lặp
        check_user = session.query(user_model).filter_by(email=data['email']).first()
        if check_user:
            response = jsonify({"message": "Email đã tồn tại trên hệ thống."}), 400
        else:
            # Khởi tạo đối tượng người dùng mới từ dữ liệu yêu cầu
            new_user = user_model(
                full_name=data.get('full_name'),
                email=data.get('email'),
                password=data.get('password'), # Ghi chú: Cần bổ sung mã hóa mật khẩu ở giai đoạn sau
                role='Student' # Mặc định phân quyền sinh viên cho tài khoản mới
            )
            session.add(new_user)
            session.commit() # Thực thi giao dịch lưu trữ vào Db HTHT
            response = jsonify({"message": "Đăng ký tài khoản thành công."}), 201
    
    except Exception as e:
        session.rollback() # Hoàn tác giao dịch nếu xảy ra lỗi trong quá trình thực thi
        response = jsonify({"message": f"Lỗi hệ thống trong quá trình đăng ký: {str(e)}"}), 500
    
    finally:
        session.close() # Giải phóng kết nối cơ sở dữ liệu
       

# ---------------------------------------------------------
# 2. API Đăng nhập hệ thống (POST /auth/login)
# ---------------------------------------------------------
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    session = SessionLocal()
    response = None

    try:
        # Xác thực danh tính người dùng qua tổ hợp Email và Mật khẩu
        user = session.query(user_model).filter_by(
            email=data['email'], 
            password=data['password']
        ).first()
        
        if not user:
            response = jsonify({"message": "Thông tin đăng nhập không chính xác."}), 401
        else:
            # Phản hồi mã truy cập tạm thời và vai trò người dùng trong hệ thống
            response = jsonify({
                "accessToken": "standard-access-token-placeholder", 
                "role": user.role,
                "message": "Đăng nhập thành công."
            }), 200
    
    finally:
        session.close()
       