from infrastructure.repositories.team_repository import TeamRepository

class TeamService:
    def __init__(self):
        # Khởi tạo instance của Repository để tương tác DB
        self.team_repo = TeamRepository()

    def create_team(self, data, user_id):
        # [LOGIC]: Data Validation (Kiểm tra dữ liệu đầu vào)
        if not data.get('name') or not data.get('class_id'):
            raise ValueError("Thiếu thông tin tên nhóm hoặc lớp học")
        
        # Gọi xuống Repository để xử lý Transaction
        return self.team_repo.create_team_with_transaction(
            name=data['name'],
            class_id=data['class_id'],
            leader_id=user_id
        )

    def register_topic(self, team_id, data, user_id):
        # Bước 1: Kiểm tra nhóm có tồn tại không
        team = self.team_repo.get_team_by_id(team_id)
        if not team:
            raise ValueError("Nhóm không tồn tại")
        
        # [ALGORITHM]: RBAC (Role-Based Access Control)
        # Giải thích: Chỉ có user đóng vai trò là 'Leader' mới có quyền ghi (Write Permission).
        if team.leader_id != user_id:
            raise PermissionError("Access Denied: Chỉ nhóm trưởng mới được đăng ký đề tài")

        project_id = data.get('project_id')
        return self.team_repo.register_topic_transaction(team_id, project_id)