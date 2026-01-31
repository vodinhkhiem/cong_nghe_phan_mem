from infrastructure.repositories.task_repository import TaskRepository

class KanbanService:
    def __init__(self):
        self.task_repo = TaskRepository()

    def get_board_data(self, workspace_id):
        """
        [ALGORITHM]: Linear Transformation / Grouping (O(N))
        Biến đổi danh sách phẳng (Flat List) thành cấu trúc phân cấp (Nested JSON).
        Chỉ duyệt qua danh sách task 1 lần duy nhất để tối ưu hiệu năng.
        """
        tasks = self.task_repo.get_tasks_by_workspace(workspace_id)
        
        # 1. Khởi tạo cấu trúc dữ liệu bảng
        board_structure = {
            "workspace_id": workspace_id,
            "columns": {
                "To Do": [],
                "In Progress": [],
                "Done": []
            }
        }
        
        # 2. Phân loại Task (Classification)
        for task in tasks:
            task_dict = {
                "id": task.id,
                "title": task.title,
                "assignee_id": task.assignee_id
            }
            
            # Logic đưa vào bucket tương ứng
            if task.status in board_structure["columns"]:
                board_structure["columns"][task.status].append(task_dict)
            else:
                board_structure["columns"]["To Do"].append(task_dict)
                
        return board_structure

    def move_task(self, task_id, target_column):
        # [LOGIC]: State Validation (Kiểm tra trạng thái đích hợp lệ)
        valid_columns = ["To Do", "In Progress", "Done", "Review"]
        if target_column not in valid_columns:
            raise ValueError(f"Invalid State: Không tồn tại cột '{target_column}'")
            
        return self.task_repo.update_task_status(task_id, target_column)