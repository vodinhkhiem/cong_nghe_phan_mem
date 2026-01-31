from infrastructure.repositories.team_repository import TeamRepository

class TeamService:
    def __init__(self):
        self.team_repo = TeamRepository()

    def create_team(self, data, user_id):
        # [VALIDATION]: Data Integrity Check
        if not data.get('name') or not data.get('class_id'):
            raise ValueError("Thiếu thông tin tên nhóm hoặc lớp học")
        
        # Gọi xuống Repo xử lý Transaction
        return self.team_repo.create_team_with_transaction(
            name=data['name'],
            class_id=data['class_id'],
            leader_id=user_id
        )

    def register_topic(self, team_id, data, user_id):
        # Bước 1: Lấy thông tin nhóm
        team = self.team_repo.get_team_by_id(team_id)
        if not team:
            raise ValueError("Nhóm không tồn tại")
        
        # [ALGORITHM]: RBAC (Role-Based Access Control)
        # Logic: Chỉ Leader mới có quyền ghi vào DB (Write Permission)
        if team.leader_id != user_id:
            raise PermissionError("Access Denied: Chỉ trưởng nhóm mới được đăng ký đề tài")

        # Bước 2: Update DB
        project_id = data.get('project_id')
        return self.team_repo.register_topic_transaction(team_id, project_id)