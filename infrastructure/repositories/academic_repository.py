from sqlalchemy.orm import Session
from infrastructure.models.academic_model import SyllabusModel, ClassModel, RubricModel, SubjectModel
from typing import Optional, List

class AcademicRepository:
    def __init__(self, session: Session):
        self.session = session

    # --- CLASS & SEMESTER ---
    def get_class_by_id(self, class_id: int) -> Optional[ClassModel]:
        return self.session.query(ClassModel).filter_by(id=class_id).first()

    # --- SYLLABUS ---
    def get_syllabus_by_subject_id(self, subject_id: int) -> Optional[SyllabusModel]:
        return self.session.query(SyllabusModel).filter_by(subject_id=subject_id).first()

    def create_syllabus(self, syllabus: SyllabusModel):
        self.session.add(syllabus)
        self.session.commit()
        return syllabus

    def update_syllabus(self, syllabus: SyllabusModel):
        self.session.commit()
        self.session.refresh(syllabus)
        return syllabus

    # --- RUBRIC ---
    def create_rubric(self, rubric: RubricModel) -> RubricModel:
        self.session.add(rubric)
        self.session.commit()
        self.session.refresh(rubric)
        return rubric

    def get_all_rubrics(self) -> List[RubricModel]:
        return self.session.query(RubricModel).order_by(RubricModel.created_at.desc()).all()