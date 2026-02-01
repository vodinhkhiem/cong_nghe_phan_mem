from datetime import datetime
import json
from infrastructure.repositories.academic_repository import AcademicRepository
from infrastructure.models.academic_model import SyllabusModel, RubricModel

class AcademicService:
    def __init__(self, repo: AcademicRepository):
        self.repo = repo

    def get_current_semester(self):
        """Logic tự động tính học kỳ dựa trên tháng hiện tại"""
        now = datetime.now()
        year = now.year
        month = now.month

        # Quy ước FPT/University:
        # Spring: 1-4, Summer: 5-8, Fall: 9-12
        if 1 <= month <= 4:
            term = "Spring"
        elif 5 <= month <= 8:
            term = "Summer"
        else:
            term = "Fall"
        
        return {
            "code": f"{term.upper()}{year}",
            "name": f"{term} {year}",
            "start_date": f"{year}-{month}-01",
            "is_active": True
        }

    def update_syllabus_for_class(self, class_id: int, data: dict):
        """
        Cập nhật Syllabus của Môn học mà lớp đó đang học.
        """
        # 1. Tìm lớp -> Tìm môn học
        clazz = self.repo.get_class_by_id(class_id)
        if not clazz:
            raise ValueError("Lớp học không tồn tại")

        # 2. Tìm Syllabus của môn đó
        syllabus = self.repo.get_syllabus_by_subject_id(clazz.subject_id)
        
        # 3. Chuẩn bị dữ liệu (Convert Dict -> JSON String)
        content = data.get('content')
        clos = json.dumps(data.get('clos')) if data.get('clos') else None
        grading = json.dumps(data.get('grading_scheme')) if data.get('grading_scheme') else None

        if syllabus:
            # Update
            if content: syllabus.content = content
            if clos: syllabus.clos = clos
            if grading: syllabus.grading_scheme = grading
            return self.repo.update_syllabus(syllabus)
        else:
            # Create
            new_syll = SyllabusModel(
                subject_id=clazz.subject_id,
                content=content,
                clos=clos,
                grading_scheme=grading
            )
            return self.repo.create_syllabus(new_syll)

    def create_rubric(self, creator_id, data):
        title = data.get('title')
        content = data.get('content') # Expecting List/Dict

        if not title or not content:
            raise ValueError("Thiếu tiêu đề hoặc nội dung Rubric")

        # Convert content sang JSON string
        content_str = json.dumps(content) if isinstance(content, (dict, list)) else str(content)

        rubric = RubricModel(
            title=title,
            description=data.get('description'),
            content=content_str,
            created_by=creator_id
        )
        return self.repo.create_rubric(rubric)

    def get_rubrics(self):
        rubrics = self.repo.get_all_rubrics()
        return [{
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "content": json.loads(r.content) if r.content else [],
            "created_at": r.created_at.isoformat() if r.created_at else None
        } for r in rubrics]