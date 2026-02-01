import difflib  # Thuật toán LCS (Longest Common Subsequence) để so sánh chuỗi
import email.utils
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

# Import Models
from infrastructure.models.collab_model import DocumentModel, WhiteboardSnapshotModel
from infrastructure.models.team_model import WorkspaceModel

# Custom Exception để Controller bắt lỗi
class VersionConflictError(Exception):
    """Bắn lỗi khi phát hiện xung đột dữ liệu (2 người cùng sửa 1 lúc)"""
    pass

class CollabService:
    
    # 1. QUẢN LÝ WORKSPACE
    @staticmethod
    def get_or_create_workspace(db: Session, team_id: int) -> WorkspaceModel:
        """
        Logic: Kiểm tra xem nhóm đã có không gian làm việc chưa.
        Nếu chưa -> Tạo mới (Lazy Initialization).
        """
        workspace = db.query(WorkspaceModel).filter(WorkspaceModel.team_id == team_id).first()
        
        if not workspace:
            workspace = WorkspaceModel(team_id=team_id)
            db.add(workspace)
            db.commit()
            db.refresh(workspace)       
        return workspace

    @staticmethod
    def get_whiteboard_state(db: Session, project_id: int):
        """
        Lấy trạng thái bảng trắng của dự án.
        """
        # Sửa: Dùng WhiteboardSnapshotModel thay vì WhiteboardModel
        board = db.query(WhiteboardSnapshotModel).filter(WhiteboardSnapshotModel.project_id == project_id).first()
        
        if not board:
            # Lazy Create: Chưa có thì tạo luôn
            board = WhiteboardSnapshotModel(project_id=project_id, data="{}")
            db.add(board)
            db.commit()
            db.refresh(board)
            
        return board.data

    @staticmethod
    def save_whiteboard_snapshot(db: Session, project_id: int, json_data: str):
        """
        Lưu trạng thái bảng (Snapshot).
        """
        board = db.query(WhiteboardSnapshotModel).filter(WhiteboardSnapshotModel.project_id == project_id).first()
        
        if not board:
            board = WhiteboardSnapshotModel(project_id=project_id, data=json_data)
            db.add(board)
        else:
            board.data = json_data # Update đè dữ liệu mới nhất lên
            board.updated_at = func.now()
            
        db.commit()
        return board

    # 3. EDITOR & CÁC THUẬT TOÁN DSA (TRỌNG TÂM ĐỒ ÁN)
    @staticmethod
    def create_document(db: Session, team_id: int, name: str, file_type: str = 'CODE'):
        workspace = CollabService.get_or_create_workspace(db, team_id)
        
        new_doc = DocumentModel(
            workspace_id=workspace.id,
            name=name,
            file_type=file_type,
            content=""
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)
        return new_doc

    @staticmethod
    def save_document_content(db: Session, doc_id: int, new_content: str, last_known_updated_at: Optional[str] = None):
        doc = db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
        if not doc:
            return False

        # --- THUẬT TOÁN KHÓA LẠC QUAN (FIXED) ---
        if last_known_updated_at and doc.updated_at:
            try:
                # 1. Parse thời gian từ Client (API trả về thường là RFC 1123 có GMT)
                client_dt = None
                try:
                    client_dt = email.utils.parsedate_to_datetime(last_known_updated_at)
                except:
                    # Fallback nếu client gửi ISO format
                    try:
                        client_dt = datetime.fromisoformat(last_known_updated_at)
                    except:
                        pass

                # 2. Lấy thời gian DB
                db_dt = doc.updated_at

                # 3. Xóa thông tin múi giờ (Make naive) để trừ được cho nhau
                if client_dt and client_dt.tzinfo:
                    client_dt = client_dt.replace(tzinfo=None)
                
                if db_dt and db_dt.tzinfo:
                    db_dt = db_dt.replace(tzinfo=None)

                # 4. So sánh lệch pha (Chấp nhận lệch < 2 giây do làm tròn API)
                if client_dt and db_dt:
                    diff = abs((db_dt - client_dt).total_seconds())
                    
                    # Nếu lệch quá 2 giây -> Có người khác đã sửa
                    if diff > 2.0: 
                        print(f"⚠️ XUNG ĐỘT: DB={db_dt} | Client={client_dt} | Diff={diff}s")
                        raise VersionConflictError("Phiên bản bạn đang sửa đã cũ.")
            
            except VersionConflictError as ve:
                raise ve # Ném lỗi ra ngoài cho Controller bắt
            except Exception as e:
                print(f"⚠️ Lỗi so sánh thời gian (Bỏ qua): {e}")
                pass 

        doc.content = new_content
        doc.updated_at = datetime.now()
        db.commit()
        return True
    
    @staticmethod
    def compare_document_versions(db: Session, doc_id: int, new_content: str):
        """
        [ALGORITHM]: DIFF / LCS (Longest Common Subsequence)
        
        Mục đích: Tìm sự khác biệt giữa phiên bản cũ và mới.
        Ứng dụng: Giống tính năng 'git diff' hoặc 'Track Changes'.
        """
        doc = db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
        if not doc:
            return None

        current_content = doc.content or ""
        
        # Sử dụng thư viện difflib (Dựa trên thuật toán LCS cải tiến)
        old_lines = current_content.splitlines()
        new_lines = new_content.splitlines()
        
        # Tạo generator so sánh
        diff = difflib.unified_diff(
            old_lines, 
            new_lines, 
            fromfile='Current Version', 
            tofile='Your Changes', 
            lineterm=''
        )
        
        # Trả về danh sách các dòng thay đổi (VD: ['- cũ', '+ mới'])
        return list(diff)

    @staticmethod
    def find_version_by_timestamp_algorithm(versions_list: list, target_timestamp: float):
        """
        [ALGORITHM]: BINARY SEARCH (Tìm kiếm nhị phân) - O(log n)
        
        Mục đích: Tìm phiên bản document gần nhất với một mốc thời gian cụ thể.
        Input: Danh sách versions đã sắp xếp theo thời gian.
        """
        left = 0
        right = len(versions_list) - 1
        closest_version = None
        min_diff = float('inf')

        while left <= right:
            mid = (left + right) // 2
            mid_obj = versions_list[mid]
            
            # Giả sử mid_obj có thuộc tính created_at (datetime)
            mid_time = mid_obj.created_at.timestamp()
            
            # Tính độ lệch
            diff = abs(mid_time - target_timestamp)
            
            if diff < min_diff:
                min_diff = diff
                closest_version = mid_obj

            if mid_time == target_timestamp:
                return mid_obj # Tìm thấy chính xác
            elif mid_time < target_timestamp:
                left = mid + 1
            else:
                right = mid - 1
                
        return closest_version

    # Các hàm Helper cơ bản
    @staticmethod
    def get_all_documents(db: Session, team_id: int):
        workspace = CollabService.get_or_create_workspace(db, team_id)
        return db.query(DocumentModel).filter(DocumentModel.workspace_id == workspace.id).all()

    @staticmethod
    def get_document_by_id(db: Session, doc_id: int):
        return db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()