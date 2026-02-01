from infrastructure.repositories.evaluation_repository import EvaluationRepository
from infrastructure.models.evaluation_model import CheckpointModel, SubmissionModel, PeerReviewModel

class EvaluationService:
    def __init__(self, repo: EvaluationRepository):
        self.repo = repo

    def submit_assignment(self, user_id, data):
        team_id = data.get('team_id')
        milestone_id = data.get('milestone_id')
        file_url = data.get('file_url')

        if not all([team_id, milestone_id, file_url]):
            raise ValueError("Thiếu thông tin nộp bài")

        # 1. Tìm hoặc Tạo Checkpoint (Chỉ gọi 1 lần)
        checkpoint = self.repo.get_checkpoint(team_id, milestone_id)
        if not checkpoint:
            checkpoint = self.repo.create_checkpoint(team_id, milestone_id)

        # 2. Kiểm tra bài cũ để Update hoặc Tạo mới
        existing_sub = self.repo.get_existing_submission(checkpoint.id)
        
        if existing_sub:
            existing_sub.file_url = file_url
            existing_sub.student_id = user_id
            self.repo.update_submission_grade(existing_sub) 
            return existing_sub
        else:
            # Tạo bài mới
            submission = SubmissionModel(
                team_id=team_id,
                checkpoint_id=checkpoint.id,
                student_id=user_id,
                file_url=file_url
            )
            saved_sub = self.repo.create_submission(submission)
            self.repo.update_checkpoint_status(checkpoint.id, 'Submitted')
            return saved_sub

    def submit_peer_review(self, reviewer_id, data):
        target_id = data.get('target_id')
        checkpoint_id = data.get('checkpoint_id')
        score = data.get('score')

        if reviewer_id == target_id:
            raise ValueError("Không thể tự đánh giá chính mình")

        review = PeerReviewModel(
            reviewer_id=reviewer_id,
            target_id=target_id,
            checkpoint_id=checkpoint_id,
            score=score,
            comment=data.get('comment')
        )
        return self.repo.create_peer_review(review)

    def instructor_grade(self, submission_id, score, feedback):
        submission = self.repo.get_submission_by_id(submission_id)
        if not submission:
            raise ValueError("Bài nộp không tồn tại")
        
        submission.score = score
        submission.feedback = feedback
        
        updated_sub = self.repo.update_submission_grade(submission)
        self.repo.update_checkpoint_status(submission.checkpoint_id, 'Graded')
        
        return updated_sub
    
    def get_my_peer_results(self, user_id):
        reviews = self.repo.get_peer_reviews_by_target(user_id)
        if not reviews:
            return {"average": 0, "reviews": []}
        
        total = sum([r.score for r in reviews])
        avg = round(total / len(reviews), 2)
        
        # Ẩn danh người review (Chỉ lấy comment và score)
        details = [{"score": r.score, "comment": r.comment} for r in reviews]
        
        return {"average": avg, "reviews": details}

    def get_all_milestones(self):
        milestones = self.repo.get_all_milestones()
        return [{
            "id": m.id,
            "title": m.name,
            "description": m.description,
            "due_date": m.deadline.isoformat() if m.deadline else None
        } for m in milestones]

    def get_student_transcript(self, student_id):
        submissions = self.repo.get_submissions_by_student(student_id)
        results = []
        for sub in submissions:
            results.append({
                "submission_id": sub.id,
                "checkpoint_id": sub.checkpoint_id,
                "file_url": sub.file_url,
                "score": sub.score,       # Điểm số
                "feedback": sub.feedback, # Nhận xét của GV
                "submitted_at": sub.submitted_at
            })
        return results