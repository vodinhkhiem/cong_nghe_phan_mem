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
from infrastructure.models.user_model import UserModel, TokenBlocklistModel
from infrastructure.models.academic_model import SubjectModel, SyllabusModel, ClassModel, ClassMemberModel, ResourceModel, RubricModel

# 2. Nhóm Team & Project
# Đã thêm TeamModel vào đầu danh sách
from infrastructure.models.team_model import TeamModel, TeamMemberModel, WorkspaceModel, TopicModel, TeamRequestModel
from infrastructure.models.project_model import ProjectModel, ProjectMilestoneModel

# 3. Nhóm Task
from infrastructure.models.task_model import (
    TaskModel, 
    TaskChecklistModel, 
    TaskActivityModel, 
    TaskCommentModel, 
    TaskAttachmentModel
)

# 4. Nhóm khác
from infrastructure.models.notification_model import NotificationModel
from infrastructure.models.messager_model import MessageModel
from infrastructure.models.evaluation_model import CheckpointModel, SubmissionModel, PeerReviewModel
from infrastructure.models.meeting_model import MeetingModel
from infrastructure.models.collab_model import DocumentModel, WhiteboardSnapshotModel
from infrastructure.models.ai_model import AIChatHistoryModel

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
            # LEVEL 1: DỮ LIỆU GỐC (Users, Subjects)
            print("--- LEVEL 1: Users & Subjects ---")
            # 1. Users
            lecturer = get_or_create(session, UserModel, {'email': "teacher@fpt.edu.vn"}, 
                                     full_name="Thay Ng Van Code", password="123", role="Lecturer", status=True)
            leader = get_or_create(session, UserModel, {'email': "leader@fpt.edu.vn"},
                                   full_name="Pham Truong Nhom", password="123", role="Student", status=True)
            member = get_or_create(session, UserModel, {'email': "member@fpt.edu.vn"},
                                   full_name="Le Thanh Vien", password="123", role="Student", status=True)

            # 2. Subjects
            subject = get_or_create(session, SubjectModel, {'code': "SWP391"},
                                    name="Do an Phat Trien Phan mem", description="Project-based Learning")

            # LEVEL 2: HỌC LIỆU (Syllabus, Resources, Classes)
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
                    res = ResourceModel(title="Slide Bai Giang Tuan 1", file_url="https://drive.../slide1.pdf", 
                                        type="PDF", subject_id=subject.id, uploader_id=lecturer.id)
                    session.add(res)
            except ImportError:
                print("   [INFO] Chưa có ResourceModel, bỏ qua.")

            # 5. Classes
            clazz = get_or_create(session, ClassModel, {'name': "SE1701_NET"},
                                  subject_id=subject.id, lecturer_id=lecturer.id, semester="Spring 2026")

            # --- TRONG FILE seed.py ---

            # LEVEL 3: LIÊN KẾT LỚP & DỰ ÁN
            print("--- LEVEL 3: Class Members, Topics & Projects ---")

            # 7. Tạo Topic (Đề tài)
            topic = get_or_create(session, TopicModel, {'name': "He thong Quan ly Do an (EduCollab)"},
                                    description="Xây dựng nền tảng hỗ trợ học tập nhóm",
                                    lecturer_id=lecturer.id,
                                    status='APPROVED',
                                    max_slots=3)

            # 8. Projects & Milestones
            project = get_or_create(session, ProjectModel, {'title': "Standard Software Process"},
                                    syllabus_id=syllabus.id, 
                                    created_by=lecturer.id,
                                    status="Approved")

            if not session.query(ProjectMilestoneModel).filter_by(project_id=project.id).first():
                m1 = ProjectMilestoneModel(
                    name="Sprint 1: Database Design",
                    description="Nộp ERD và Script SQL", 
                    deadline=datetime.now() + timedelta(days=7),
                    project_id=project.id 
                )
                m2 = ProjectMilestoneModel(
                    name="Sprint 2: Backend API", 
                    description="Hoàn thiện module Auth và User", 
                    deadline=datetime.now() + timedelta(days=14),
                    project_id=project.id
                )
                session.add_all([m1, m2])
                session.flush() 
                print("✅ [NEW] Seeded 2 Project Milestones")
                milestone1 = m1 
            else:
                milestone1 = session.query(ProjectMilestoneModel).filter_by(project_id=project.id).first()

            # LEVEL 4: NHÓM & KHÔNG GIAN LÀM VIỆC
            print("--- LEVEL 4: Teams & Workspaces ---")

            # 9. Teams
            team = get_or_create(session, TeamModel, {'name': "Team 1 - Dragon"},
                                class_id=clazz.id, 
                                project_id=topic.id, 
                                leader_id=leader.id)

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

            # LEVEL 5: TIẾN ĐỘ & NỘP BÀI (Checkpoints, Submissions, Reviews)
            print("--- LEVEL 5: Grading & Checkpoints ---")
            
            # Cần import các model mới này. Nếu chưa có file, bạn cần tạo class model tương ứng.
            try:
                from infrastructure.models.evaluation_model import CheckpointModel, SubmissionModel, PeerReviewModel
                
                # Lúc này milestone1.id đã có giá trị từ Level 3
                checkpoint = session.query(CheckpointModel).filter_by(team_id=team.id, milestone_id=milestone1.id).first()
                if not checkpoint:
                    checkpoint = CheckpointModel(team_id=team.id, milestone_id=milestone1.id, status="Open")
                    session.add(checkpoint)
                    session.flush()
                
                # 13. Submissions (Nộp bài)
                if not session.query(SubmissionModel).filter_by(checkpoint_id=checkpoint.id, student_id=leader.id).first():
                    sub = SubmissionModel(team_id=team.id, checkpoint_id=checkpoint.id, student_id=leader.id, 
                                          file_url="github.com/project", score=9.5)
                    session.add(sub)
                
                # 14. Peer Reviews (Đánh giá chéo)
                if not session.query(PeerReviewModel).filter_by(reviewer_id=leader.id, target_id=member.id).first():
                    rev = PeerReviewModel(reviewer_id=leader.id, target_id=member.id, checkpoint_id=checkpoint.id, 
                                          score=10, comment="Lam viec rat cham chi")
                    session.add(rev)

            except ImportError:
                print("   [INFO] Chưa có các Model Grading (Checkpoint, Submission...), bỏ qua Level 5.")

            # LEVEL 6: COLLAB & COMMUNICATION (Docs, Meet, Messages...)
            print("--- LEVEL 6: Real-time Features ---")

            # 15. Documents
            if not session.query(DocumentModel).filter_by(workspace_id=workspace.id).first():
                doc = DocumentModel(
                    workspace_id=workspace.id, 
                    name="app.py", 
                    content="from flask import Flask\n\napp = Flask(__name__)\n\n@app.route('/')\ndef hello():\n    return 'Hello World'", 
                    file_type="CODE"
                )
                session.add(doc)
                print(f"   [NEW]  Tạo mới documents: {doc.name}")

            # 16. Whiteboard Snapshots
            if project:
                if not session.query(WhiteboardSnapshotModel).filter_by(project_id=project.id).first():
                    wb = WhiteboardSnapshotModel(
                        project_id=project.id, 
                        # Init data rỗng chuẩn cho Frontend đỡ lỗi
                        data='{"shapes": [], "bindings": {}, "assets": {}}' 
                    )
                    session.add(wb)
                    print(f"   [NEW]  Tạo mới whiteboard cho Project ID: {project.id}")

            # 17. Tasks (Kanban)
            task = get_or_create(session, TaskModel, {'title': "Thiet ke Database", 'workspace_id': workspace.id}, 
                                status="Done", assignee_id=leader.id, priority="High", position=1)

            task2 = get_or_create(session, TaskModel, {'title': "Viet code API Task", 'workspace_id': workspace.id}, 
                                status="In Progress", assignee_id=member.id, priority="Medium", position=2)

            # SEED CHECKLIST
            if not session.query(TaskChecklistModel).filter_by(task_id=task2.id).first():
                session.add(TaskChecklistModel(task_id=task2.id, content="Tao Model", is_done=True))
                session.add(TaskChecklistModel(task_id=task2.id, content="Tao Controller", is_done=False))
                print("   [NEW]  Tao checklist cho Task 2")

            # SEED ACTIVITY
            if not session.query(TaskActivityModel).filter_by(task_id=task2.id).first():
                session.add(TaskActivityModel(task_id=task2.id, user_id=leader.id, action="da giao task cho Le Thanh Vien"))
                session.add(TaskActivityModel(task_id=task2.id, user_id=member.id, action="da bat dau lam task"))

            # SEED COMMENT
            if not session.query(TaskCommentModel).filter_by(task_id=task2.id).first():
                session.add(TaskCommentModel(task_id=task2.id, user_id=member.id, content="Database xong chua sep?"))

            # Giả lập 1 file PDF đính kèm vào Task 2
            if not session.query(TaskAttachmentModel).filter_by(task_id=task2.id).first():
                attachment = TaskAttachmentModel(
                    task_id=task2.id,
                    url="https://example.com/files/design-spec-v1.pdf",
                    name="Design_Specification_v1.pdf"
                )
                session.add(attachment)
                print("   [NEW]  Đã đính kèm file mẫu vào Task 2")
            # 18. Meetings
            if not session.query(MeetingModel).filter_by(team_id=team.id).first():
                meet = MeetingModel(team_id=team.id, creator_id=leader.id, title="Hop dau tuan", 
                                    start_time=datetime.now(), end_time=datetime.now() + timedelta(hours=1), is_online=True)
                session.add(meet)

            # 19. Messages
            if not session.query(MessageModel).filter_by(team_id=team.id).first():
                msg = MessageModel(team_id=team.id, sender_id=member.id, content="Code xong chưa sep oi?")
                session.add(msg)

            # 20. Notifications (Thông báo)
            try:
                from infrastructure.models.notification_model import NotificationModel
                if not session.query(NotificationModel).filter_by(user_id=leader.id).first():
                    notif = NotificationModel(user_id=leader.id, title="Deadline", message="Sap den han nop bai", type="Alert")
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