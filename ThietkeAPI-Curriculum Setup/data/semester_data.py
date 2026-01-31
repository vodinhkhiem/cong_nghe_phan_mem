# data/semester_data.py
# Lưu dữ liệu học kỳ (giả lập DB)

from models.semester import Semester

class SemesterData:
    def __init__(self):
        self.semesters = [
            Semester("S1", "Semester 1 - 2023"),
            Semester("S2", "Semester 2 - 2024", True)  # học kỳ hiện tại
        ]

    def get_current_semester(self):
        # Linear Search (Giải thuật: tìm tuyến tính)
        for semester in self.semesters:
            if semester.is_current:
                return semester
        return None
