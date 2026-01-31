from flask import Flask
from .config import Config
from .api.middleware import middleware
from .api.routes import register_routes
from .infrastructure.databases import init_db
from .app_logging import setup_logging

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    setup_logging(app)
    init_db(app)
    middleware(app)
    register_routes(app)

    return app