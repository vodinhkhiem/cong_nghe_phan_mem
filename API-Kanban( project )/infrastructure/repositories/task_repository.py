from sqlalchemy.exc import SQLAlchemyError
from infrastructure.databases.mssql import session
from infrastructure.models.task_model import TaskModel

class TaskRepository:
    def get_tasks_by_workspace(self, workspace_id):
        # [QUERY PATTERN]: Filtering (Lọc dữ liệu)
        # Lấy toàn bộ task thuộc về một workspace/project cụ thể
        return session.query(TaskModel).filter_by(workspace_id=workspace_id).all()

    def update_task_status(self, task_id, new_status):
        try:
            # Tìm task theo ID
            task = session.query(TaskModel).filter_by(id=task_id).first()
            if task:
                # [LOGIC]: Update field status
                task.status = new_status
                session.commit()
                return task
            return None
        except Exception as e:
            session.rollback()
            raise e