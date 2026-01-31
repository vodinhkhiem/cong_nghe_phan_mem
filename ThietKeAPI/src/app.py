from flask import Flask, jsonify
# from api.routes import register_routes
from api.swagger import spec

from api.middleware import middleware
from api.responses import success_response
from infrastructure.databases import init_db
from config import Config
from flasgger import Swagger
from config import SwaggerConfig
from flask_swagger_ui import get_swaggerui_blueprint
from api.controllers.team_controller import team_bp
from api.controllers.kanban_controller import kanban_bp

def create_app():
    app = Flask(__name__)
    Swagger(app)
    
    # Đăng ký Blueprint mới vào Flask 
    app.register_blueprint(team_bp, url_prefix='/api')
    app.register_blueprint(kanban_bp, url_prefix='/api')

    # Thêm Swagger UI blueprint
    SWAGGER_URL = '/docs'
    API_URL = '/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={'app_name': "Todo API"}
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    try:
        init_db(app)
    except Exception as e:
        print(f"Error initializing database: {e}")

    # Register middleware
    middleware(app)

    # Register routes to Swagger
    with app.test_request_context():
        for rule in app.url_map.iter_rules():
            # Thêm tên blueprint 'team_bp' và 'kanban_bp' vào danh sách này để Swagger tự động quét và hiện API lên docs
            if rule.endpoint.startswith(('todo.', 'course.', 'user.', 'auth.', 'team_bp.', 'kanban_bp.')):
                view_func = app.view_functions[rule.endpoint]
                print(f"Adding path: {rule.rule} -> {view_func}")
                spec.path(view=view_func)
            
    @app.route("/swagger.json")
    def swagger_json():
        return jsonify(spec.to_dict())

    return app

# Run the application
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=9999, debug=True)