from flask import Blueprint, jsonify

analytics_bp = Blueprint("analytics_bp", __name__)

@analytics_bp.route("/analytics", methods=["GET"])
def get_analytics():
    data = {
        "users": 120,
        "orders": 45,
        "revenue": 1500000
    }
    return jsonify(data)
