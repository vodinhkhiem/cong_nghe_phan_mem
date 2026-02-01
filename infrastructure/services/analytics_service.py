from infrastructure.repositories.analytics_repository import AnalyticsRepository

class AnalyticsService:
    def __init__(self, repo: AnalyticsRepository):
        self.repo = repo

    def get_student_dashboard(self, user_id: int):
        """
        Aggregation API: Deadlines sắp tới, Task đang làm.
        """
        deadlines = self.repo.get_upcoming_deadlines(user_id)
        tasks = self.repo.get_active_tasks(user_id)
        
        return {
            "upcoming_deadlines": [{
                "id": m.id,
                "name": m.name,
                "deadline": m.deadline.isoformat() if m.deadline else None
            } for m in deadlines],
            "active_tasks": [{
                "id": t.id,
                "title": t.title,
                "status": t.status,
                "due_date": t.due_date.isoformat() if t.due_date else None
            } for t in tasks],
            # Thông báo có thể lấy từ bảng Notification (nếu có)
            "new_notifications": [] 
        }

    def get_lecturer_dashboard(self, lecturer_id: int):
        """
        Aggregation API: Số bài cần chấm, Các nhóm chậm tiến độ.
        """
        pending_count = self.repo.count_pending_submissions(lecturer_id)
        lagging_teams = self.repo.get_lagging_teams(lecturer_id)
        
        return {
            "pending_grading_count": pending_count,
            "lagging_teams": [{
                "team_id": t.id,
                "team_name": t.name,
                "class_name": t.class_name,
                "overdue_tasks": t.overdue_count
            } for t in lagging_teams]
        }

    def get_clo_attainment(self):
        """
        Thống kê mức độ đạt chuẩn đầu ra (Trưởng bộ môn).
        Note: Ở đây giả định lấy thống kê chung, thực tế cần tham số subject_id.
        """
        return {
            "subject_id": 0,
            "average_score": 75.0  # Giá trị giả lập
        }