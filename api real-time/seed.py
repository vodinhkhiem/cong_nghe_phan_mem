import sys
import os
from datetime import datetime, timedelta

# 1. Cấu hình đường dẫn
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import Config
from infrastructure.databases.mssql import init_mssql, engine
from sqlalchemy.orm import Session

# --- IMPORT TẤT CẢ MODEL ---
# Import từ 'infrastructure...' sẽ hoạt động vì file này nằm trong 'src'
# 1. Nhóm Core (User, Academic)
from infrastructure.models.user_model import UserModel
from infrastructure.models.academic_model import SubjectModel, SyllabusModel, ClassModel, ClassMemberModel, ResourceModel

# 2. Nhóm Team & Project
# Đã thêm TeamModel vào đầu danh sách
from infrastructure.models.team_model import TeamModel, TeamMemberModel, WorkspaceModel
from infrastructure.models.project_model import ProjectModel, ProjectMilestoneModel

# 3. Nhóm Task
from infrastructure.models.task_model import TaskModel

# 4. Nhóm khác
from infrastructure.models.notification_model import NotificationModel
from infrastructure.models.messager_model import MessageModel
from infrastructure.models.evaluation_model import CheckpointModel, SubmissionModel, PeerReviewModel
from infrastructure.models.meeting_model import MeetingModel
from infrastructure.models.collab_model import DocumentModel, WhiteboardSnapshotModel

# --- HÀM HELPER ĐỂ TRÁNH TRÙNG LẶP ---
# --- HÀM HELPER ĐỂ TRÁNH TRÙNG LẶP (ĐÃ SỬA LỖI) ---
def get_or_create(session, model, check_columns, **kwargs):
    # 1. Kiểm tra xem dữ liệu đã tồn tại chưa
    instance = session.query(model).filter_by(**check_columns).first()
    
    if instance:
        print(f"   [SKIP] {model.__tablename__} đã có: {list(check_columns.values())[0]}")
        return instance
    else:
        # 2. Quan trọng: Gộp dữ liệu tìm kiếm (check_columns) vào dữ liệu tạo mới (kwargs)
        create_data = kwargs.copy()
        create_data.update(check_columns) 
        
        instance = model(**create_data)
        session.add(instance)
        session.flush()
        print(f"   [NEW]  Tạo mới {model.__tablename__}: {list(check_columns.values())[0]}")
        return instance

def seed_database():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_mssql(app)

    with app.app_context():
        session = Session(bind=engine)
        print("\n=== BẮT ĐẦU SEED DATA (FULL 20 TABLES) ===\n")

        try:
            # ====================================================
            # LEVEL 1: DỮ LIỆU GỐC (Users, Subjects)
            # ====================================================
            print("--- LEVEL 1: Users & Subjects ---")
            
            # 1. Users
            lecturer = get_or_create(session, UserModel, {'email': "teacher@fpt.edu.vn"}, 
                                     full_name="Thầy Nguyễn Văn Code", password="123", role="Lecturer", status=True)
            leader = get_or_create(session, UserModel, {'email': "leader@fpt.edu.vn"},
                                   full_name="Phạm Trưởng Nhóm", password="123", role="Student", status=True)
            member = get_or_create(session, UserModel, {'email': "member@fpt.edu.vn"},
                                   full_name="Lê Thành Viên", password="123", role="Student", status=True)

            # 2. Subjects
            subject = get_or_create(session, SubjectModel, {'code': "SWP391"},
                                    name="Đồ án Phát triển Phần mềm", description="Project-based Learning")

            # ====================================================
            # LEVEL 2: HỌC LIỆU (Syllabus, Resources, Classes)
            # ====================================================
            print("--- LEVEL 2: Academic Content ---")

            # 3. Syllabuses
            syllabus = session.query(SyllabusModel).filter_by(subject_id=subject.id).first()
            if not syllabus:
                syllabus = SyllabusModel(subject_id=subject.id, content="1. Intro, 2. Design, 3. Code, 4. Deploy")
                session.add(syllabus)
                session.flush()

            # 4. Resources (Tài nguyên môn học)
            try:
                from infrastructure.models.academic_model import ResourceModel
                if not session.query(ResourceModel).filter_by(subject_id=subject.id).first():
                    res = ResourceModel(title="Slide Bài Giảng Tuần 1", file_url="https://drive.../slide1.pdf", 
                                        type="PDF", subject_id=subject.id, uploader_id=lecturer.id)
                    session.add(res)
            except ImportError:
                print("   [INFO] Chưa có ResourceModel, bỏ qua.")

            # 5. Classes
            clazz = get_or_create(session, ClassModel, {'name': "SE1701_NET"},
                                  subject_id=subject.id, lecturer_id=lecturer.id, semester="Spring 2026")

            # ====================================================
            # LEVEL 3: LIÊN KẾT LỚP & DỰ ÁN (ClassMembers, Projects)
            # ====================================================
            print("--- LEVEL 3: Class Members & Projects ---")

            # 6. Class Members
            for student in [leader, member]:
                if not session.query(ClassMemberModel).filter_by(class_id=clazz.id, student_id=student.id).first():
                    session.add(ClassMemberModel(class_id=clazz.id, student_id=student.id))

            # 7. Projects
            project = get_or_create(session, ProjectModel, {'title': "Hệ thống Quản lý Đồ án (EduCollab)"},
                                    syllabus_id=syllabus.id, created_by=lecturer.id, status="Approved")

            # 8. Project Milestones (Các cột mốc dự án)
            # LƯU Ý: due_week là bắt buộc (NOT NULL) như lỗi lần trước
            if not session.query(ProjectMilestoneModel).filter_by(project_id=project.id).first():
                m1 = ProjectMilestoneModel(project_id=project.id, name="Sprint 1", description="Database & UI", due_week=2)
                m2 = ProjectMilestoneModel(project_id=project.id, name="Sprint 2", description="API & Integration", due_week=5)
                session.add_all([m1, m2])
                session.flush()
                milestone1 = m1
            else:
                milestone1 = session.query(ProjectMilestoneModel).filter_by(project_id=project.id, name="Sprint 1").first()
                assert milestone1 is not None, "Lỗi: Không tìm thấy Milestone 1!"

            # ====================================================
            # LEVEL 4: NHÓM & KHÔNG GIAN LÀM VIỆC (Teams, Workspaces)
            # ====================================================
            print("--- LEVEL 4: Teams & Workspaces ---")

            # 9. Teams
            team = get_or_create(session, TeamModel, {'name': "Team 1 - Dragon"},
                                 class_id=clazz.id, project_id=project.id, leader_id=leader.id)

            # 10. Team Members
            if not session.query(TeamMemberModel).filter_by(team_id=team.id, user_id=leader.id).first():
                session.add(TeamMemberModel(team_id=team.id, user_id=leader.id, role='Leader'))
            if not session.query(TeamMemberModel).filter_by(team_id=team.id, user_id=member.id).first():
                session.add(TeamMemberModel(team_id=team.id, user_id=member.id, role='Member'))

            # 11. Workspaces
            workspace = session.query(WorkspaceModel).filter_by(team_id=team.id).first()
            if not workspace:
                workspace = WorkspaceModel(team_id=team.id)
                session.add(workspace)
                session.flush()

            # ====================================================
            # LEVEL 5: TIẾN ĐỘ & NỘP BÀI (Checkpoints, Submissions, Reviews)
            # ====================================================
            print("--- LEVEL 5: Grading & Checkpoints ---")
            
            # Cần import các model mới này. Nếu chưa có file, bạn cần tạo class model tương ứng.
            try:
                from infrastructure.models.evaluation_model import CheckpointModel, SubmissionModel, PeerReviewModel
                
                # 12. Checkpoints (Điểm kiểm tra của nhóm cho cột mốc 1)
                checkpoint = session.query(CheckpointModel).filter_by(team_id=team.id, milestone_id=milestone1.id).first()
                if not checkpoint:
                    checkpoint = CheckpointModel(team_id=team.id, milestone_id=milestone1.id, status="Open")
                    session.add(checkpoint)
                    session.flush()
                
                # 13. Submissions (Nộp bài)
                if not session.query(SubmissionModel).filter_by(checkpoint_id=checkpoint.id, student_id=leader.id).first():
                    sub = SubmissionModel(checkpoint_id=checkpoint.id, student_id=leader.id, 
                                          file_url="github.com/project", score=9.5)
                    session.add(sub)
                
                # 14. Peer Reviews (Đánh giá chéo)
                if not session.query(PeerReviewModel).filter_by(reviewer_id=leader.id, target_id=member.id).first():
                    rev = PeerReviewModel(reviewer_id=leader.id, target_id=member.id, checkpoint_id=checkpoint.id, 
                                          score=10, comment="Làm việc rất chăm chỉ")
                    session.add(rev)

            except ImportError:
                print("   [INFO] Chưa có các Model Grading (Checkpoint, Submission...), bỏ qua Level 5.")

            # ====================================================
            # LEVEL 6: COLLAB & COMMUNICATION (Docs, Meet, Messages...)
            # ====================================================
            print("--- LEVEL 6: Real-time Features ---")

            # 15. Documents
            if not session.query(DocumentModel).filter_by(workspace_id=workspace.id).first():
                doc = DocumentModel(workspace_id=workspace.id, name="app.py", content="from flask import Flask...", file_type="CODE")
                session.add(doc)

            # 16. Whiteboard Snapshots
            if not session.query(WhiteboardSnapshotModel).filter_by(workspace_id=workspace.id).first():
                wb = WhiteboardSnapshotModel(workspace_id=workspace.id, data='{"shapes": []}')
                session.add(wb)

            # 17. Tasks (Kanban)
            if not session.query(TaskModel).filter_by(workspace_id=workspace.id).first():
                task = TaskModel(workspace_id=workspace.id, title="Thiết kế Database", status="Done", 
                                 assignee_id=leader.id, priority="High")
                session.add(task)

            # 18. Meetings
            if not session.query(MeetingModel).filter_by(team_id=team.id).first():
                meet = MeetingModel(team_id=team.id, creator_id=leader.id, title="Họp đầu tuần", 
                                    start_time=datetime.now(), end_time=datetime.now() + timedelta(hours=1), is_online=True)
                session.add(meet)

            # 19. Messages
            if not session.query(MessageModel).filter_by(team_id=team.id).first():
                msg = MessageModel(team_id=team.id, sender_id=member.id, content="Code xong chưa sếp ơi?")
                session.add(msg)

            # 20. Notifications (Thông báo)
            try:
                from infrastructure.models.notification_model import NotificationModel
                if not session.query(NotificationModel).filter_by(user_id=leader.id).first():
                    notif = NotificationModel(user_id=leader.id, title="Deadline", message="Sắp đến hạn nộp bài", type="Alert")
                    session.add(notif)
            except ImportError:
                 print("   [INFO] Chưa có NotificationModel, bỏ qua.")

            # === HOÀN TẤT ===
            session.commit()
            print("\n✅ SEED DATA COMPLETED SUCCESSFULLY!")
            print(f"👉 Team ID để test: {team.id}")
            print(f"👉 Project ID: {project.id}")
        
        except Exception as e:
            session.rollback()
            print(f"\n❌ LỖI LỚN KHI SEED DATA: {e}")
            print("💡 Gợi ý: Kiểm tra xem các file Model đã được import đúng chưa.")
        finally:
            session.close()

if __name__ == "__main__":
    seed_database()