from infrastructure.databases.mssql import SessionLocal
from infrastructure.repositories.task_repository import TaskRepository
from infrastructure.models.task_model import TaskModel

class TaskService:
    def __init__(self, repository):
        self.repo = repository

    def create_task(self, data, creator_id):
        # 1. Tạo đối tượng TaskModel từ data
        new_task = TaskModel(
            title=data.get('title'),
            description=data.get('description'),
            workspace_id=data.get('workspace_id'),
            status=data.get('status', 'To Do'),
            priority=data.get('priority', 'Medium'),
            assignee_id=data.get('assignee_id'),
            position=0
        )
        
        # 2. Gọi hàm add chuẩn của Repo
        return self.repo.add(new_task)

    def list_tasks(self, team_id):
        if hasattr(self.repo, 'list_by_team'):
            return self.repo.list_by_team(team_id)
        return []

    def get_task_detail(self, task_id):
        return self.repo.get_by_id(task_id)

    def update_task(self, task_id, data, user_id):
        task = self.repo.get_by_id(task_id)
        if task:
            if 'title' in data: task.title = data['title']
            if 'description' in data: task.description = data['description']
            if 'status' in data: task.status = data['status']
            if 'assignee_id' in data: task.assignee_id = data['assignee_id']
            self.repo.session.commit()
            return task
        return None

    def delete_task(self, task_id, user_id):
        if hasattr(self.repo, 'delete'):
            return self.repo.delete(task_id)
        return False

    def move_task(self, task_id, target_column, new_pos, user_id):
        task = self.repo.get_by_id(task_id)
        if not task:
            raise ValueError("Task not found")
        old_status = task.status
        self.repo.update_position_and_status(task_id, target_column, new_pos)
        self.repo.add_activity(task_id, user_id, f"đã chuyển từ '{old_status}' sang '{target_column}'")
        return True
    
    def get_board_data(self, workspace_id):
        """Phân loại task vào 4 cột: To Do, In Progress, Review, Done"""
        tasks = self.repo.get_tasks_by_workspace(workspace_id)
        board = {
            "workspace_id": workspace_id,
            "columns": {"To Do": [], "In Progress": [], "Review": [], "Done": []}
        }
        for t in tasks:
            task_data = {
                "id": t.id,
                "title": t.title,
                "position": t.position,
                "assignee": t.assignee_id,
                "progress": {
                    "total": len(t.checklists),
                    "done": len([c for c in t.checklists if c.is_done])
                }
            }
            if t.status in board["columns"]:
                board["columns"][t.status].append(task_data)
        return board

    def toggle_checklist(self, checklist_id):
        return self.repo.toggle_checklist_item(checklist_id)

    def add_comment(self, task_id, user_id, content):
        self.repo.add_activity(task_id, user_id, "đã thêm một bình luận")
        return self.repo.add_comment(task_id, user_id, content)