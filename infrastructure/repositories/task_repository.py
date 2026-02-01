from domain.models.itodo_repository import ITodoRepository
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from infrastructure.models.task_model import TaskModel, TaskActivityModel, TaskChecklistModel, TaskCommentModel, TaskAttachmentModel

class TaskRepository(ITodoRepository):
    def __init__(self, session: Session):
        # Không dùng biến toàn cục để tránh lỗi xung đột thread/session
        self.session = session

    def add(self, task_data: TaskModel) -> TaskModel:
        """
        Thêm mới một Task. 
        Lưu ý: task_data đã bao gồm assignee_id và team_id từ Service gửi xuống.
        """
        try:
            self.session.add(task_data)
            self.session.commit()
            self.session.refresh(task_data)
            return task_data
        except Exception as e:
            self.session.rollback()
            raise e
        # Không close() session ở đây vì session thường được quản lý theo Request (Middleware)

    def get_by_id(self, task_id: int) -> Optional[TaskModel]:
        return self.session.query(TaskModel).filter_by(id=task_id).first()

    def list_by_team(self, team_id: int) -> List[TaskModel]:
        """Lấy danh sách task theo nhóm (Quan trọng cho đồ án)"""
        return self.session.query(TaskModel)\
            .options(joinedload(TaskModel.assignee))\
            .filter_by(team_id=team_id).all()

    def list(self) -> List[TaskModel]:
        """Lấy toàn bộ tasks (Select * from tasks)"""
        return self.session.query(TaskModel).all()

    def update(self, task_id: int, update_data: dict) -> Optional[TaskModel]:
        """
        Cập nhật Task dựa trên dict dữ liệu.
        Cách này tốt hơn là mapping thủ công từng trường.
        """
        try:
            task = self.get_by_id(task_id)
            if task:
                for key, value in update_data.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                self.session.commit()
                self.session.refresh(task)
                return task
            return None
        except Exception as e:
            self.session.rollback()
            raise e

    def delete(self, task_id: int) -> bool:
        try:
            task = self.get_by_id(task_id)
            if task:
                self.session.delete(task)
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            raise e

    def update_position_and_status(self, task_id, new_status, new_pos):
        """Logic chèn Task và đẩy các Task khác để tránh trùng vị trí"""
        task = self.get_by_id(task_id)
        if not task: return

        # 1. Thu dọn khoảng trống ở cột cũ (giảm position của các task đứng sau)
        self.session.query(TaskModel).filter(
            and_(TaskModel.status == task.status, TaskModel.position > task.position)
        ).update({TaskModel.position: TaskModel.position - 1})

        # 2. Tạo khoảng trống ở cột mới (tăng position của các task đứng sau vị trí mới)
        self.session.query(TaskModel).filter(
            and_(TaskModel.status == new_status, TaskModel.position >= new_pos)
        ).update({TaskModel.position: TaskModel.position + 1})

        # 3. Cập nhật task hiện tại
        task.status = new_status
        task.position = new_pos
        self.session.commit()

    def add_activity(self, task_id, user_id, action):
        """Ghi vết cho API /tasks/{id}/activities"""
        activity = TaskActivityModel(
            task_id=task_id,
            user_id=user_id,
            action=action
        )
        self.session.add(activity)
        self.session.commit()

    def get_activities(self, task_id):
        """Lấy lịch sử để hiển thị trên UI Kanban"""
        return self.session.query(TaskActivityModel)\
            .filter_by(task_id=task_id)\
            .order_by(TaskActivityModel.created_at.desc()).all()

    def create_checklist_item(self, task_id, content):
        """Dùng cho tính năng chia nhỏ Task (Scaffolding)"""
        item = TaskChecklistModel(task_id=task_id, content=content)
        self.session.add(item)
        self.session.commit()
        return item

    def get_tasks_by_workspace(self, workspace_id):
        """Lấy danh sách task kèm theo checklist để hiển thị board"""
        return self.session.query(TaskModel)\
            .options(joinedload(TaskModel.checklists))\
            .filter_by(workspace_id=workspace_id)\
            .order_by(TaskModel.position.asc()).all()

    def toggle_checklist_item(self, checklist_id):
        item = self.session.get(TaskChecklistModel, checklist_id)
        if item:
            item.is_done = not item.is_done
            self.session.commit()
        return item

    def add_comment(self, task_id, user_id, content):
        comment = TaskCommentModel(task_id=task_id, user_id=user_id, content=content)
        self.session.add(comment)
        self.session.commit()
        return comment

    def add_attachment(self, task_id, file_url, file_name):
        attachment = TaskAttachmentModel(task_id=task_id, url=file_url, name=file_name)
        self.session.add(attachment)
        self.session.commit()
        return attachment