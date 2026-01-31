from infrastructure.databases.mssql import session
from infrastructure.models.task_model import TaskModel

class TaskRepository:
    def get_tasks_by_workspace(self, workspace_id):
        # [QUERY]: Filtering (Lọc dữ liệu theo Workspace/Project)
        return session.query(TaskModel).filter_by(workspace_id=workspace_id).all()

    def update_task_status(self, task_id, new_status):
        try:
            # [QUERY]: Search & Update
            task = session.query(TaskModel).filter_by(id=task_id).first()
            if task:
                task.status = new_status
                session.commit()
                return task
            return None
        except Exception as e:
            session.rollback()
            raise e