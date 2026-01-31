# File: app.py
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys

# 1. Load biến môi trường (API Key) từ file .env
load_dotenv()

# 2. Thêm đường dẫn để import module (tránh lỗi ModuleNotFound)
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 3. Import các Blueprint
from analytics_get import analytics_bp
from ai_post import ai_bp

def create_app():
    app = Flask(__name__)
    
    # Cấu hình để Flask trả về tiếng Việt có dấu chuẩn xác
    app.config['JSON_AS_ASCII'] = False
    
    # Kích hoạt CORS (để Frontend React/Vue gọi được)
    CORS(app)

    # 4. Đăng ký Blueprint
    # Analytics: Route trong file này khá lộn xộn (/dashboard, /analytics) nên ta không set url_prefix chung
    app.register_blueprint(analytics_bp) 
    
    # AI: Tất cả route trong ảnh đều bắt đầu bằng /ai, nên ta set prefix ở đây cho gọn code con
    app.register_blueprint(ai_bp, url_prefix='/ai')

    return app

if __name__ == "__main__":
    app = create_app()
    print("🚀 Server LMS đang chạy tại http://localhost:5000")
    app.run(debug=True, port=5000)