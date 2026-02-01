# Configuration settings for the Flask application

import os
import urllib.parse  # Thư viện để xử lý ký tự đặc biệt trong mật khẩu

# --- 1. XỬ LÝ KẾT NỐI DATABASE CHUẨN ---
# Lấy thông tin từ biến môi trường (đã khai báo trong docker-compose)
# Nếu không tìm thấy thì dùng giá trị mặc định (dự phòng)
DB_SERVER = os.environ.get('DB_SERVER', 'db-sql') 
DB_USER = os.environ.get('DB_USER', 'sa')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'Khiem1234Khiem@')
DB_NAME = os.environ.get('DB_NAME', 'HTHT')

# Mã hóa mật khẩu để tránh lỗi ký tự '@'
encoded_password = urllib.parse.quote_plus(DB_PASSWORD)

# Tạo chuỗi kết nối hoàn chỉnh
# Format: mssql+pymssql://user:password@server:1433/database
CONN_STR = f"mssql+pymssql://{DB_USER}:{encoded_password}@{DB_SERVER}:1433/{DB_NAME}"

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret_key_bao_mat_123'
    DEBUG = False
    TESTING = False
    
    # Quan trọng: Flask-SQLAlchemy cần biến này chính xác
    SQLALCHEMY_DATABASE_URI = CONN_STR
    DATABASE_URI = CONN_STR
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    CORS_HEADERS = 'Content-Type'

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    DATABASE_URI = os.environ.get('DATABASE_URI') or 'mssql+pymssql://sa:Aa%40123456@127.0.0.1:1433/FlaskApiDB'


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
class SwaggerConfig:
    """Swagger configuration."""
    template = {
        "swagger": "2.0",
        "info": {
            "title": "Todo API",
            "description": "API for managing todos",
            "version": "1.0.0"
        },
        "basePath": "/",
        "schemes": [
            "http",
            "https"
        ],
        "consumes": [
            "application/json"
        ],
        "produces": [
            "application/json"
        ]
    }

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs"
    }