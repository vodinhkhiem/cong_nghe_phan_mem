from infrastructure.repositories.task_repository import TaskRepository

class KanbanService:
    def __init__(self):
        self.task_repo = TaskRepository()

    def get_board_data(self, workspace_id):
        # Lấy danh sách task dạng phẳng từ DB
        tasks = self.task_repo.get_tasks_by_workspace(workspace_id)
        
        # Khởi tạo cấu trúc dữ liệu bảng Kanban (Nested Dictionary)
        board_structure = {
            "workspace_id": workspace_id,
            "columns": {
                "To Do": [],
                "In Progress": [],
                "Done": []
            }
        }
        
        # [ALGORITHM]: Linear Transformation / Grouping (O(N) Complexity)
        # Giải thích: Duyệt qua danh sách task 1 lần duy nhất để phân loại vào các cột tương ứng.
        # Thay vì dùng nhiều câu query (Select where status=...), ta dùng thuật toán gom nhóm trên RAM để tối ưu tốc độ.
        for task in tasks:
            task_dict = {
                "id": task.id,
                "title": task.title,
                "assignee_id": task.assignee_id
            }
            
            # Logic phân loại (Classification Logic)
            if task.status in board_structure["columns"]:
                board_structure["columns"][task.status].append(task_dict)
            else:
                # Fallback: Nếu status lạ, đưa về To Do
                board_structure["columns"]["To Do"].append(task_dict)
                
        return board_structure

    def move_task(self, task_id, target_column):
        # [LOGIC]: State Validation (Kiểm tra trạng thái hợp lệ)
        # Đảm bảo task chỉ được chuyển sang các cột cho phép, tránh lỗi dữ liệu.
        valid_columns = ["To Do", "In Progress", "Done", "Review"]
        if target_column not in valid_columns:
            raise ValueError(f"Invalid State: Cột '{target_column}' không hợp lệ")
            
        return self.task_repo.update_task_status(task_id, target_column)