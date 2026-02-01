from flask import Flask, jsonify
from sqlalchemy import text
from flasgger import Swagger
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
# 1. Import socketio từ file extensions
from extensions import socketio 
# 2. Import file events để code socket chạy
import events.socket_events

# Import Config
from config import Config, SwaggerConfig

# 1. Import Spec
from api.swagger import spec

# 2. Import Controllers
from api.controllers.collab_controller import collab_bp
from api.controllers.communication_controller import comm_bp
from api.controllers.team_controller import team_bp
from api.controllers.task_controller import bp as task_bp
from api.controllers.auth_controller import auth_bp
from api.controllers.user_controller import user_bp
from api.controllers.evaluation_controller import evaluation_bp
from api.controllers.academic_controller import academic_bp
from api.controllers.ai_controller import ai_bp
from api.controllers.analytics_controller import analytics_bp

# 3. Import Middleware và Response
from api.middleware import setup_middlewares
from api.responses import success_response

# 4. Database
from infrastructure.databases.mssql import init_mssql, engine


# Khởi tạo Flask App
def create_app():
    # Khởi tạo App
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources={r"/*": {"origins": "*"}})
    setup_middlewares(app)

    # --- SETUP 1: FLASGGER ---
    swagger = Swagger(app, 
                      config=SwaggerConfig.swagger_config, 
                      template=SwaggerConfig.template)
                      
    socketio.init_app(app, cors_allowed_origins="*")

    # --- SETUP 2: ĐĂNG KÝ BLUEPRINT ---
    app.register_blueprint(collab_bp)
    app.register_blueprint(comm_bp)
    app.register_blueprint(team_bp)
    app.register_blueprint(task_bp) 
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(evaluation_bp)
    app.register_blueprint(academic_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(analytics_bp)

    # --- SETUP 3: SWAGGER UI (Option) ---
    # SWAGGER_URL = '/docs'
    # API_URL = '/swagger.json'
    # swaggerui_blueprint = get_swaggerui_blueprint(
    #     SWAGGER_URL,
    #     API_URL,
    #     config={'app_name': "Todo API"}
    # )
    # app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # --- SETUP 4: CORS ---

    # Khởi tạo Database
    with app.app_context():
        try:
            init_mssql(app)
            print("✅ MSSQL Initialized successfully from mssql.py")
        except Exception as e:
            print(f"⚠️ Warning: {e}")

    # Route test kết nối
    @app.route("/test_db")
    def test_db():
        """
        Kiểm tra kết nối Database SQL Server
        ---
        tags:
          - System
        responses:
          200:
            description: Kết nối thành công
        """
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                return jsonify({"message": "✅ KẾT NỐI DATABASE THÀNH CÔNG!"})
        except Exception as e:
            return jsonify({"error": str(e)})

    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, host='0.0.0.0', port=9999, debug=True, allow_unsafe_werkzeug=True)