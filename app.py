from flask import Flask
import sys
import os

# thêm src vào path
sys.path.append(os.path.dirname(__file__))

from analytics_get import analytics_bp
from ai_post import ai_bp

app = Flask(__name__)

app.register_blueprint(analytics_bp)
app.register_blueprint(ai_bp)

if __name__ == "__main__":
    app.run(debug=True)
