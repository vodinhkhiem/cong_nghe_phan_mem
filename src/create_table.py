import sys
import os
from sqlalchemy import text

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
from infrastructure.models.user_model import UserModel, TokenBlocklistModel
from infrastructure.models.academic_model import (
    SubjectModel, SyllabusModel, ClassModel, ClassMemberModel, ResourceModel, RubricModel
)

# 2. Nhóm Team & Project
# Đã thêm TeamModel vào đầu danh sách
from infrastructure.models.team_model import TeamModel, TeamMemberModel, WorkspaceModel, TopicModel, TeamRequestModel
from infrastructure.models.project_model import ProjectModel, ProjectMilestoneModel

# 3. Nhóm Task
from infrastructure.models.task_model import (
    TaskModel, TaskChecklistModel, TaskActivityModel, TaskCommentModel, TaskAttachmentModel
)

# 4. Nhóm khác
from infrastructure.models.notification_model import NotificationModel
from infrastructure.models.messager_model import MessageModel
from infrastructure.models.evaluation_model import CheckpointModel, SubmissionModel, PeerReviewModel
from infrastructure.models.meeting_model import MeetingModel, MeetingAttendeeModel
from infrastructure.models.collab_model import DocumentModel, WhiteboardSnapshotModel
from infrastructure.models.ai_model import AIChatHistoryModel

def create_tables():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_mssql(app)
    print("⏳ Đang kết nối tới SQL Server...")
    with app.app_context():
        try:
            with engine.connect() as connection:

                # 1: XÓA SẠCH KHÓA NGOẠI (FOREIGN KEYS)
                print("🔗 Đang cắt bỏ toàn bộ Khóa ngoại (Foreign Keys)...")
                drop_fk_script = """
                DECLARE @sql NVARCHAR(MAX) = N'';
                SELECT @sql += N'ALTER TABLE ' + QUOTENAME(OBJECT_SCHEMA_NAME(parent_object_id))
                    + '.' + QUOTENAME(OBJECT_NAME(parent_object_id)) + 
                    ' DROP CONSTRAINT ' + QUOTENAME(name) + ';'
                FROM sys.foreign_keys;
                EXEC sp_executesql @sql;
                """
                connection.execute(text(drop_fk_script))
                
                # 2: XÓA SẠCH CÁC BẢNG (DROP TABLES)
                print("🗑️ Đang xóa toàn bộ bảng cũ (Force Drop)...")
                drop_tables_script = """
                DECLARE @sql2 NVARCHAR(MAX) = N'';
                SELECT @sql2 += N'DROP TABLE ' + QUOTENAME(TABLE_SCHEMA) + '.' + QUOTENAME(TABLE_NAME) + ';'
                FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';
                EXEC sp_executesql @sql2;
                """
                connection.execute(text(drop_tables_script))
                connection.commit()

            # 3: TẠO LẠI TỪ ĐẦU
            # Lúc này DB đã trắng tinh, không cần gọi drop_all() của SQLAlchemy nữa
            print("🔨 Đang tạo bảng mới...")
            Base.metadata.create_all(bind=engine)
            
            print("✅ Đã cập nhật Database thành công (Full Tables)!")
            
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    create_tables()