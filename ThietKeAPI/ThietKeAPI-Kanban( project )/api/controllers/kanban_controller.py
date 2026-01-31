from flask import Blueprint, request, jsonify
from services.kanban_service import KanbanService

kanban_bp = Blueprint('kanban_bp', __name__)
kanban_service = KanbanService()

@kanban_bp.route('/workspaces/<int:workspace_id>/board', methods=['GET'])
def get_board(workspace_id):
    try:
        data = kanban_service.get_board_data(workspace_id)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@kanban_bp.route('/tasks/<int:task_id>/move', methods=['PUT'])
def move_task(task_id):
    try:
        data = request.json
        target_column = data.get('targetColumnId')
        kanban_service.move_task(task_id, target_column)
        return jsonify({"message": "Cập nhật vị trí thành công"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400