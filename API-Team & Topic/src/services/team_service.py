from infrastructure.repositories.team_repository import TeamRepository

class TeamService:
    def __init__(self):
        self.team_repo = TeamRepository()

    # 1. LOGIC NHÓM (TEAM)
    def create_team(self, data, user_id):
        # [LOGIC]: Validation
        if not data.get('name') or not data.get('class_id'):
            raise ValueError("Thiếu thông tin tên nhóm/lớp")
        return self.team_repo.create_team_with_transaction(data['name'], data['class_id'], user_id)

    def leave_team(self, team_id, user_id):
        # [RULE]: Leader không được rời nếu chưa chuyển quyền
        team = self.team_repo.get_team_by_id(team_id)
        if not team: raise ValueError("Nhóm không tồn tại")
        
        if team.leader_id == user_id:
            raise ValueError("Leader không thể rời nhóm. Hãy xóa nhóm hoặc chuyển quyền Leader trước.")
            
        success = self.team_repo.remove_member(team_id, user_id)
        if not success: raise ValueError("Bạn không phải thành viên nhóm này")
        return True

    # 2. LOGIC ĐỀ TÀI (TOPIC)
    def create_topic(self, data, user_id, user_role):
        """
        Logic tạo đề tài:
        - Nếu là GV (Lecturer): Status = Approved (Được dùng luôn)
        - Nếu là SV: Status = Pending (Chờ GV duyệt)
        """
        is_gv = (user_role == 'Lecturer')
        status = 'Approved' if is_gv else 'Pending'
        
        return self.team_repo.create_topic(
            title=data.get('title'),
            description=data.get('description'),
            created_by=user_id,
            is_gv=is_gv,
            status=status
        )

    def approve_topic(self, topic_id, user_role):
        """[RBAC]: Chỉ Giảng viên mới được duyệt đề tài"""
        if user_role != 'Lecturer':
            raise PermissionError("Chỉ Giảng viên mới được quyền duyệt đề tài")
        
        topic = self.team_repo.get_topic_by_id(topic_id)
        if not topic: raise ValueError("Đề tài không tồn tại")
        
        topic.status = 'Approved'
        return self.team_repo.update_topic(topic)

    def get_topics(self):
        return self.team_repo.get_all_topics()

    def register_topic_for_team(self, team_id, data, user_id):
        """Leader đăng ký một đề tài ĐÃ DUYỆT cho nhóm"""
        team = self.team_repo.get_team_by_id(team_id)
        if team.leader_id != user_id:
            raise PermissionError("Chỉ Leader mới được đăng ký đề tài")
        
        topic_id = data.get('project_id')
        topic = self.team_repo.get_topic_by_id(topic_id)
        
        # [LOGIC]: Chỉ được chọn đề tài đã Approved
        if not topic or topic.status != 'Approved':
            raise ValueError("Đề tài không tồn tại hoặc chưa được duyệt")
            
        return self.team_repo.assign_topic_to_team(team_id, topic_id)

    # 3. LOGIC THÀNH VIÊN (MEMBERSHIP)
    def request_to_join(self, team_id, user_id):
        """SV xin vào nhóm"""
        if self.team_repo.get_team_member(team_id, user_id):
            raise ValueError("Bạn đã là thành viên nhóm này")
        
        return self.team_repo.create_request(team_id, user_id, type='JOIN')

    def invite_member(self, team_id, target_user_id, requester_id):
        """[RBAC]: Chỉ Leader mới được mời thành viên"""
        team = self.team_repo.get_team_by_id(team_id)
        if team.leader_id != requester_id:
            raise PermissionError("Chỉ Leader mới được mời thành viên")
        
        if self.team_repo.get_team_member(team_id, target_user_id):
            raise ValueError("Người này đã ở trong nhóm")
            
        return self.team_repo.create_request(team_id, target_user_id, type='INVITE')

    def respond_to_request(self, request_id, action, user_id):
        """
        Xử lý duyệt/từ chối:
        - Case 1 (JOIN): SV xin vào -> Leader duyệt.
        - Case 2 (INVITE): Leader mời -> SV được mời đồng ý.
        """
        req = self.team_repo.get_request_by_id(request_id)
        if not req or req.status != 'Pending':
            raise ValueError("Yêu cầu không hợp lệ hoặc đã được xử lý")

        team = self.team_repo.get_team_by_id(req.team_id)
        is_approved = (action == 'approve')

        # [LOGIC]: Phân quyền ai được duyệt
        if req.type == 'JOIN':
            if team.leader_id != user_id:
                raise PermissionError("Chỉ Leader mới được duyệt đơn xin vào")
        elif req.type == 'INVITE':
            if req.user_id != user_id:
                raise PermissionError("Bạn không phải là người nhận lời mời này")

        return self.team_repo.resolve_request_transaction(req, is_approved)