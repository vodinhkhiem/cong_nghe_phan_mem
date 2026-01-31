from flask import Blueprint, request, jsonify
from services.kanban_service import KanbanService

kanban_bp = Blueprint('kanban_bp', __name__)
kanban_service = KanbanService()

@kanban_bp.route('/workspaces/<int:workspace_id>/board', methods=['GET'])
def get_board(workspace_id):
    """
    API Lấy dữ liệu bảng Kanban để hiển thị lên UI.
    ---
    tags:
      - Kanban Board
    """
    try:
        # Gọi Service để lấy dữ liệu đã được gom nhóm (Grouped Data)
        data = kanban_service.get_board_data(workspace_id)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@kanban_bp.route('/tasks/<int:task_id>/move', methods=['PUT'])
def move_task(task_id):
    """
    API Kéo thả Task (Drag & Drop Update).
    """
    try:
        data = request.json
        target_column = data.get('targetColumnId')
        
        # Cập nhật trạng thái mới cho Task
        kanban_service.move_task(task_id, target_column)
        return jsonify({"message": "Cập nhật vị trí thành công"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
