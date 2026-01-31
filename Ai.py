from flask import Blueprint, request, jsonify

ai_bp = Blueprint("ai_bp", __name__)

@ai_bp.route("/ai", methods=["POST"])
def ai_process():
    data = request.json

    if not data or "text" not in data:
        return jsonify({"error": "Missing text"}), 400

    result = f"AI processed: {data['text']}"
    return jsonify({"result": result})
