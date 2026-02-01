from flask import Blueprint, request, jsonify
from infrastructure.models import CheckpointModel, SubmissionModel, PeerReviewModel, user_model
from infrastructure.databases.mssql import SessionLocal 

evaluation_bp = Blueprint('evaluation', __name__)

# ---------------------------------------------------------
# 1. Truy xuất danh sách cột mốc nộp bài (GET /milestones)
# ---------------------------------------------------------
@evaluation_bp.route('/milestones', methods=['GET'])
def get_milestones():
    session = SessionLocal()
    
    try:
        # Truy vấn toàn bộ dữ liệu từ bảng Checkpoints trong cơ sở dữ liệu
        milestones = session.query(CheckpointModel).all()
        data = []
        for ms in milestones:
            data.append({
                "id": ms.id,
                "title": f"Cột mốc {ms.id}",  # Định dạng tiêu đề hiển thị
                "status": ms.status
            })
        return jsonify(data), 200
    
    except Exception as e:
        return jsonify({"message": f"Lỗi truy xuất dữ liệu: {str(e)}"}), 500
    
    finally:
        session.close()  # Giải phóng tài nguyên kết nối


# ---------------------------------------------------------
# 2. Xử lý nộp bài làm của nhóm (POST /submissions)
# ---------------------------------------------------------
@evaluation_bp.route('/submissions', methods=['POST'])
def create_submission():
    data = request.json
    session = SessionLocal()
    
    try:
        # Khởi tạo đối tượng Submission mới từ dữ liệu yêu cầu
        new_sub = SubmissionModel(
            checkpoint_id=data.get('checkpoint_id'),
            student_id=data.get('student_id'),
            file_url=data.get('file_url')
        )
        session.add(new_sub)
        session.commit()  # Xác nhận giao dịch lưu trữ vào cơ sở dữ liệu
        return jsonify({"message": "Đã thực hiện nộp bài thành công."}), 201
    
    except Exception as e:
        session.rollback()  # Hoàn tác giao dịch nếu phát sinh ngoại lệ
        return jsonify({"message": f"Lỗi trong quá trình nộp bài: {str(e)}"}), 500
    
    finally:
        session.close()


# ---------------------------------------------------------
# 3. Đánh giá chéo thành viên trong nhóm (POST /peer-evaluations)
# ---------------------------------------------------------
@evaluation_bp.route('/peer-evaluations', methods=['POST'])
def peer_evaluate():
    data = request.json
    session = SessionLocal()
    
    try:
        # Ghi nhận kết quả đánh giá năng lực giữa các thành viên
        new_review = PeerReviewModel(
            student_id=data.get('targetUserId'),
            score=data.get('scores'),
            comment=data.get('comment')
        )
        session.add(new_review)
        session.commit()
        return jsonify({"message": "Ghi nhận đánh giá thành viên thành công."}), 200
    
    except Exception as e:
        session.rollback()
        return jsonify({"message": f"Lỗi hệ thống khi đánh giá: {str(e)}"}), 500
    
    finally:
        session.close()


# ---------------------------------------------------------
# 4. Giảng viên thực hiện chấm điểm bài nộp (POST /grades/instructor)
# ---------------------------------------------------------
@evaluation_bp.route('/grades/instructor', methods=['POST'])
def grade_submission():
    data = request.json
    session = SessionLocal()
    
    try:
        # Truy vấn bài nộp cụ thể theo định danh (ID)
        submission = session.query(SubmissionModel).filter_by(id=data.get('submission_id')).first()
        
        if not submission:
            return jsonify({"message": "Không tìm thấy dữ liệu bài nộp để chấm điểm."}), 404
        
        # Cập nhật điểm số và nhận xét từ giảng viên vào cơ sở dữ liệu
        submission.score = data.get('score')
        submission.feedback = data.get('feedback')
        session.commit()
        return jsonify({"message": "Đã cập nhật điểm số và phản hồi thành công."}), 200
    
    except Exception as e:
        session.rollback()
        return jsonify({"message": f"Lỗi trong quá trình chấm điểm: {str(e)}"}), 500
    
    finally:
        session.close()





       
       