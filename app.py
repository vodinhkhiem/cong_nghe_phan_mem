from flask import Flask, jsonify
from domain.models import course, todo, user
from api.swagger import spec
from api.controllers.todo_controller import bp as todo_bp

# 1. Import các Blueprint mới từ thư mục controllers
from api.controllers.auth_controller import auth_bp
from api.controllers.user_controller import user_bp
from api.controllers.evaluation_controller import evaluation_bp

from api.middleware import middleware
from api.responses import success_response
from infrastructure.databases import init_db
from config import Config
from flasgger import Swagger
from config import SwaggerConfig
from flask_swagger_ui import get_swaggerui_blueprint


def create_app():
    app = Flask(__name__)
    Swagger(app)
    
    # 2. Đăng ký các Blueprint vào hệ thống
    app.register_blueprint(todo_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(evaluation_bp)

     # Cấu hình Swagger UI
    SWAGGER_URL = '/docs'
    API_URL = '/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={'app_name': "CollabSphere API"} # Đổi tên dự án cho chuyên nghiệp
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    try:
        # Khởi tạo Database và tạo bảng tự động
        init_db(app)
    except Exception as e:
        print(f"Error initializing database: {e}")

    # Kích hoạt Middleware
    middleware(app)

    # 3. Cập nhật vòng lặp quét Endpoint để Swagger hiển thị đầy đủ
    with app.test_request_context():
        for rule in app.url_map.iter_rules():
            # Thêm 'auth.' và 'evaluation.' để spec.path nhận diện được
            if rule.endpoint.startswith(('todo.', 'course.', 'user.', 'auth.', 'evaluation.')):
                view_func = app.view_functions[rule.endpoint]
                print(f"Adding path: {rule.rule} -> {view_func}")
                spec.path(view=view_func)

    @app.route("/swagger.json")
    def swagger_json():
        return jsonify(spec.to_dict())

    return app

# Khởi chạy ứng dụng
if __name__ == '__main__':
    app = create_app()
    # Chạy trên cổng 9999 như ông đã cấu hình
    app.run(host='0.0.0.0', port=9999, debug=True)
    