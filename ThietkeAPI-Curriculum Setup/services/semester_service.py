# services/semester_service.py
# Xử lý nghiệp vụ Semester

from data.semester_data import SemesterData

class SemesterService:
    def __init__(self):
        self.data = SemesterData()

    def get_current_semester(self):
        # API: GET /semesters/current
        return self.data.get_current_semester()
