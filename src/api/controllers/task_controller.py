from flask import Blueprint, request, jsonify, g
from infrastructure.databases.mssql import SessionLocal 
from infrastructure.repositories.task_repository import TaskRepository
from infrastructure.services.task_service import TaskService
from api.middleware import auth_required

bp = Blueprint('todo', __name__, url_prefix='/api/v1/tasks')

def get_service():
    """
    Sử dụng Scoped Session để đảm bảo tính nhất quán.
    Không cần đóng thủ công trong hàm vì sẽ đóng ở cleanup.
    """
    session = SessionLocal() 
    repo = TaskRepository(session)
    return TaskService(repo)

# 1. LẤY TẤT CẢ TASK CỦA TEAM
@bp.route('/team/<int:team_id>', methods=['GET'])
@auth_required
def list_tasks(team_id):
    service = get_service()
    tasks = service.list_tasks(team_id)
    return jsonify([{
        "id": t.id, 
        "title": t.title, 
        "status": t.status, 
        "assignee_id": t.assignee_id
    } for t in tasks]), 200

# 2. TẠO TASK MỚI
@bp.route('/', methods=['POST'])
@auth_required
def create_task():
    service = get_service()
    data = request.json
    # g.user_id lấy từ Auth Middleware
    new_task = service.create_task(data, g.user_id)
    return jsonify({"message": "Created", "id": new_task.id}), 201

# 3. LẤY CHI TIẾT TASK
# 3a. LẤY CHI TIẾT 1 TASK
@bp.route('/<int:task_id>', methods=['GET']) # Đúng route: /api/v1/tasks/{id}
@auth_required
def get_task_detail(task_id):
    service = get_service()
    task = service.get_task_detail(task_id) # Gọi đúng hàm Detail
    if task:
        return jsonify({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status
        }), 200
    return jsonify({"message": "Not found"}), 404

# 3b. LẤY DỮ LIỆU BẢNG KANBAN
@bp.route('/project/<int:project_id>/board', methods=['GET'])
@auth_required
def get_board(project_id):
    """
    Lấy toàn bộ dữ liệu bảng Kanban
    ---
    tags:
      - Kanban
    security:
      - Bearer: []
    parameters:
      - name: project_id
        in: path
        type: integer
    responses:
      200:
        description: JSON chứa danh sách cột và tasks
    """
    service = get_service()
    data = service.get_board_data(project_id) 
    return jsonify(data), 200

# 4. CẬP NHẬT TASK
@bp.route('/<int:task_id>', methods=['PUT'])
@auth_required
def update_task(task_id):
    service = get_service()
    data = request.json 
    updated_task = service.update_task(task_id, data, g.user_id)       
    if updated_task:
        return jsonify({"message": "Success"}), 200
    return jsonify({"message": "Not found or update failed"}), 404

# 5. XÓA TASK
@bp.route('/<int:task_id>', methods=['DELETE'])
@auth_required
def delete_task(task_id):
    service = get_service()
    success = service.delete_task(task_id, g.user_id)
    if not success:
        return jsonify({"error": "Delete failed"}), 400
    return jsonify({"message": "Deleted"}), 200

# 7. DI CHUYỂN TASK (DRAG & DROP)
@bp.route('/<int:task_id>/move', methods=['PUT'])
@auth_required
def move_task(task_id):
    """
    Cập nhật vị trí Task (Kéo thả)
    ---
    tags:
      - Kanban
    security:
      - Bearer: []
    parameters:
      - name: task_id
        in: path
        type: integer
      - in: body
        name: body
        schema:
          type: object
          properties:
            targetColumnId: {type: string}
            newPosition: {type: integer}
    responses:
      200:
        description: Di chuyển thành công
    """
    service = get_service()
    data = request.json
    service.move_task(task_id, data['targetColumnId'], data.get('newPosition', 0), g.user_id)
    return jsonify({"message": "Moved"}), 200

# 8. QUẢN LÝ CHECKLIST
@bp.route('/<int:task_id>/checklist', methods=['POST'])
@auth_required
def add_checklist(task_id):
    service = get_service()
    content = request.json.get('content')
    item = service.repo.create_checklist_item(task_id, content)
    return jsonify({"id": item.id, "content": item.content}), 201

@bp.route('/checklist/<int:checklist_id>/toggle', methods=['PUT'])
@auth_required
def toggle_checklist(checklist_id):
    service = get_service()
    item = service.toggle_checklist(checklist_id)
    return jsonify({"is_done": item.is_done}), 200

# 9. LẤY NHẬT KÝ HOẠT ĐỘNG
@bp.route('/<int:task_id>/activities', methods=['GET'])
@auth_required
def list_activities(task_id):
    service = get_service()
    activities = service.repo.get_activities(task_id)
    return jsonify([{
        "user": a.user.full_name, 
        "action": a.action, 
        "time": a.created_at.isoformat()
    } for a in activities]), 200

# 10. THẢO LUẬN (COMMENTS)
@bp.route('/<int:task_id>/comments', methods=['POST'])
@auth_required
def add_comment(task_id):
    service = get_service()
    content = request.json.get('content')
    comment = service.add_comment(task_id, g.user_id, content)
    return jsonify({"id": comment.id, "content": comment.content}), 201

@bp.route('/<int:task_id>/attachments', methods=['POST'])
@auth_required
def add_attachment(task_id):
    service = get_service()
    data = request.json
    attachment = service.repo.add_attachment(task_id, data['url'], data['name'])
    return jsonify({"id": attachment.id, "url": attachment.url}), 201
# --- QUẢN LÝ TÀI NGUYÊN TỰ ĐỘNG ---
@bp.after_request
def cleanup(response):
    """
    Hàm này chạy SAU KHI JSON đã được gửi đi.
    Giải phóng kết nối Database an toàn.
    """
    SessionLocal.remove()
    return response