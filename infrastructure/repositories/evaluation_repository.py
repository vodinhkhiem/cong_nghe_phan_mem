from sqlalchemy.orm import Session
from infrastructure.models.evaluation_model import CheckpointModel, SubmissionModel, PeerReviewModel
from typing import Optional, List
from infrastructure.models.project_model import ProjectMilestoneModel

class EvaluationRepository:
    def __init__(self, session: Session):
        self.session = session

    # --- MILESTONE ---
    def get_all_milestones(self):
        return self.session.query(ProjectMilestoneModel).all() 

    # --- CHECKPOINT ---
    def get_checkpoint(self, team_id: int, milestone_id: int) -> Optional[CheckpointModel]:
        return self.session.query(CheckpointModel).filter_by(
            team_id=team_id, milestone_id=milestone_id
        ).first()

    def create_checkpoint(self, team_id: int, milestone_id: int) -> CheckpointModel:
        ckpt = CheckpointModel(team_id=team_id, milestone_id=milestone_id, status='Open')
        self.session.add(ckpt)
        self.session.commit()
        return ckpt

    def update_checkpoint_status(self, checkpoint_id: int, status: str):
        ckpt = self.session.query(CheckpointModel).filter_by(id=checkpoint_id).first()
        if ckpt:
            ckpt.status = status
            self.session.commit()

    # --- SUBMISSION ---
    def create_submission(self, submission: SubmissionModel) -> SubmissionModel:
        self.session.add(submission)
        self.session.commit()
        self.session.refresh(submission)
        return submission

    def get_submission_by_id(self, sub_id: int) -> Optional[SubmissionModel]:
        return self.session.query(SubmissionModel).filter_by(id=sub_id).first()

    def update_submission_grade(self, submission: SubmissionModel):
        self.session.commit()
        return submission

    def get_existing_submission(self, checkpoint_id: int) -> Optional[SubmissionModel]:
        return self.session.query(SubmissionModel).filter_by(checkpoint_id=checkpoint_id).first()
    
    def get_submissions_by_student(self, student_id: int) -> List[SubmissionModel]:
        return self.session.query(SubmissionModel).filter_by(student_id=student_id).all()

    # --- PEER REVIEW ---
    def create_peer_review(self, review: PeerReviewModel):
        self.session.add(review)
        self.session.commit()
        return review

    def get_peer_reviews_by_target(self, target_id: int) -> List[PeerReviewModel]:
        return self.session.query(PeerReviewModel).filter_by(target_id=target_id).all()
