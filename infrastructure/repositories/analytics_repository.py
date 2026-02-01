from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_
from datetime import datetime

# Import các Models cần thiết (Giả định đã có từ các module trước)
from infrastructure.models.task_model import TaskModel
from infrastructure.models.evaluation_model import SubmissionModel, GradeModel
from infrastructure.models.project_model import ProjectMilestoneModel
from infrastructure.models.team_model import TeamModel, TeamMemberModel, WorkspaceModel
from infrastructure.models.academic_model import ClassModel, SubjectModel

class AnalyticsRepository:
    def __init__(self, session: Session):
        self.session = session

    # --- STUDENT DASHBOARD ---
    def get_upcoming_deadlines(self, user_id: int):
        """Lấy các cột mốc (Milestone) sắp đến hạn của team mà user tham gia"""
        return self.session.query(ProjectMilestoneModel)\
            .join(TeamModel, TeamModel.project_id == ProjectMilestoneModel.project_id)\
            .join(TeamMemberModel, TeamMemberModel.team_id == TeamModel.id)\
            .filter(TeamMemberModel.user_id == user_id)\
            .filter(ProjectMilestoneModel.deadline >= datetime.now())\
            .order_by(ProjectMilestoneModel.deadline.asc())\
            .limit(5).all()

    def get_active_tasks(self, user_id: int):
        """Lấy các Task đang làm (TODO/IN_PROGRESS) của user"""
        return self.session.query(TaskModel)\
            .filter(TaskModel.assignee_id == user_id)\
            .filter(TaskModel.status.in_(['TODO', 'IN_PROGRESS', 'To Do', 'In Progress']))\
            .order_by(TaskModel.due_date.asc()) \
            .limit(10).all()

    # --- LECTURER DASHBOARD ---
    def count_pending_submissions(self, lecturer_id: int):
        """Đếm số bài nộp chưa chấm điểm của các lớp giảng viên dạy"""
        return self.session.query(func.count(SubmissionModel.id))\
            .join(TeamModel, SubmissionModel.team_id == TeamModel.id)\
            .join(ClassModel, TeamModel.class_id == ClassModel.id)\
            .filter(ClassModel.lecturer_id == lecturer_id)\
            .filter(SubmissionModel.score == None)\
            .scalar()

    def get_lagging_teams(self, lecturer_id: int):
        """
        Tìm các nhóm chậm tiến độ.
        Logic: Nhóm có nhiều Task quá hạn (Overdue) chưa hoàn thành.
        """
        now = datetime.now()
        return self.session.query(
                TeamModel.id, 
                TeamModel.name, 
                ClassModel.name.label("class_name"),
                func.count(TaskModel.id).label("overdue_count")
            )\
            .join(ClassModel, TeamModel.class_id == ClassModel.id)\
            .join(WorkspaceModel, WorkspaceModel.team_id == TeamModel.id)\
            .join(TaskModel, TaskModel.workspace_id == WorkspaceModel.id)\
            .filter(ClassModel.lecturer_id == lecturer_id)\
            .filter(TaskModel.due_date < now) \
            .filter(TaskModel.status != 'DONE')\
            .filter(TaskModel.status != 'Done')\
            .group_by(TeamModel.id, TeamModel.name, ClassModel.name)\
            .having(func.count(TaskModel.id) > 0)\
            .order_by(func.count(TaskModel.id).desc())\
            .limit(5).all()

    # --- SUBJECT ANALYTICS ---
    def get_clo_attainment(self, subject_id: int):
        """
        Thống kê điểm trung bình theo môn học (Giả lập map với CLO).
        """
        return self.session.query(
            func.avg(GradeModel.score).label("avg_score")
        ).join(SubmissionModel, GradeModel.submission_id == SubmissionModel.id)\
         .join(TeamModel, SubmissionModel.team_id == TeamModel.id)\
         .join(ClassModel, TeamModel.class_id == ClassModel.id)\
         .filter(ClassModel.subject_id == subject_id)\
         .scalar()