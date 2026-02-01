import sys
import os

# Đảm bảo Python nhìn thấy thư mục src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from infrastructure.databases.base import Base
from infrastructure.databases.mssql import engine
from infrastructure.databases.mssql import init_mssql
from config import Config
from flask import Flask

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

# ... Import tiếp các model khác (Course, Appointment...) ...

def create_tables():
    # 2. Tạo App giả để nạp cấu hình (ConnectionString)
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 3. Khởi tạo Engine kết nối
    init_mssql(app)
    
    print("⏳ Đang kết nối tới SQL Server...")
    
    # 4. Chạy lệnh tạo bảng trong App Context
    with app.app_context():
        try:
            Base.metadata.create_all(bind=engine)
            print("✅ Đã tạo bảng thành công! Hãy kiểm tra Azure Data Studio.")
        except Exception as e:
            print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    create_tables()