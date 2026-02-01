from sqlalchemy.orm import Session
from datetime import datetime
from infrastructure.models import CheckpointModel, SubmissionModel, PeerReviewModel


class EvaluationService:
    # ---------------------------------------------------------
    # 1. QUẢN LÝ CỘT MỐC (MILESTONES)
    # ---------------------------------------------------------
    @staticmethod
    def get_all_milestones(db: Session):
        """Truy xuất và sắp xếp các cột mốc theo ID (hoặc thời gian)"""
        return db.query(CheckpointModel).order_by(CheckpointModel.id).all()
    
    # ---------------------------------------------------------
    # 2. QUẢN LÝ NỘP BÀI (SUBMISSIONS)
    # ---------------------------------------------------------
    @staticmethod
    def submit_assignment(db: Session, checkpoint_id: int, student_id: int, file_url: str):
        """
        Logic: Kiểm tra xem sinh viên đã nộp bài cho cột mốc này chưa.
        Nếu đã nộp -> Cập nhật link mới. Nếu chưa -> Tạo bản ghi mới.
        """
        existing_sub = db.query(SubmissionModel).filter(
            SubmissionModel.checkpoint_id == checkpoint_id,
            SubmissionModel.student_id == student_id
        ).first()
        
        if existing_sub:
            existing_sub.file_url = file_url
            existing_sub.updated_at = datetime.now()
            submission = existing_sub
        else:
            submission = SubmissionModel(
                checkpoint_id=checkpoint_id,
                student_id=student_id,
                file_url=file_url
            )
            db.add(submission)
        
        db.commit()
        db.refresh(submission)
        return submission
    
    # ---------------------------------------------------------
    # 3. THUẬT TOÁN TÍNH ĐIỂM TRUNG BÌNH ĐÁNH GIÁ CHÉO (ALGORITHM)
    # ---------------------------------------------------------
    @staticmethod
    def calculate_average_peer_score(db: Session, target_student_id: int):
        """
        [ALGORITHM]: Aggregation / Mean Calculation
        Mục đích: Tính điểm trung bình cộng mà các thành viên khác chấm cho student này.
        """
        reviews = db.query(PeerReviewModel).filter(
            PeerReviewModel.student_id == target_student_id
        ).all()
        
        if not reviews:
            return 0.0
        
        total_score = sum([r.score for r in reviews])
        return round(total_score / len(reviews), 2)
    
    # ---------------------------------------------------------
    # 4. THUẬT TOÁN TÌM KIẾM BÀI NỘP THEO ID (BINARY SEARCH)
    # ---------------------------------------------------------
    @staticmethod
    def find_submission_fast(submissions_list: list, target_id: int):
        """
        [ALGORITHM]: BINARY SEARCH - O(log n)
        Mục đích: Tìm nhanh một bài nộp trong danh sách đã sắp xếp theo ID.
        """
        low = 0
        high = len(submissions_list) - 1
        
        while low <= high:
            mid = (low + high) // 2
            
            if submissions_list[mid].id == target_id:
                return submissions_list[mid]
            elif submissions_list[mid].id < target_id:
                low = mid + 1
            else:
                high = mid - 1
        
        return None