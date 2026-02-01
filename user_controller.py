from flask import Blueprint, request, jsonify
from infrastructure.models import user_model 
from infrastructure.databases.mssql import SessionLocal 

user_bp = Blueprint('user', __name__)

# ---------------------------------------------------------
# 1. API Truy xuất hồ sơ cá nhân (GET /users/profile)
# ---------------------------------------------------------
@user_bp.route('/profile', methods=['GET'])
def get_profile():
    session = SessionLocal()
    response = None
    
    try:
        # Truy vấn thông tin người dùng hiện tại (Mặc định lấy bản ghi đầu tiên để kiểm thử)
        user = session.query(user_model).first() 
        
        if not user:
            response = jsonify({"message": "Không tìm thấy dữ liệu hồ sơ."}), 404
        else:
            # Trả về các thông tin cơ bản phục vụ hiển thị trên giao diện Profile
            response = jsonify({
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role,
                "avatar_url": user.avatar_url,
                "description": user.description
            }), 200
    
    finally:
        session.close()
        

# ---------------------------------------------------------
# 2. API Cập nhật thông tin hồ sơ (PUT /users/profile)
# ---------------------------------------------------------
@user_bp.route('/profile', methods=['PUT'])
def update_profile():
    data = request.json
    session = SessionLocal()
    response = None

    try:
        user = session.query(user_model).first()
        if not user:
            response = jsonify({"message": "Người dùng không tồn tại."}), 404
        else:
            # Cập nhật các trường thông tin cho phép thay đổi như Ảnh đại diện và Mô tả
            if 'avatar_url' in data:
                user.avatar_url = data['avatar_url']
            if 'description' in data:
                user.description = data['description']
                
            session.commit() # Ghi nhận thay đổi vào cơ sở dữ liệu
            response = jsonify({"message": "Cập nhật hồ sơ thành công."}), 200
            
    except Exception as e:
        session.rollback()
        response = jsonify({"message": f"Lỗi cập nhật dữ liệu: {str(e)}"}), 500
        
    finally:
        session.close()
       
       