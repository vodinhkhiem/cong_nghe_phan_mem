# data/syllabus_data.py
# Dữ liệu đề cương

from models.syllabus import Syllabus

class SyllabusData:
    def __init__(self):
        self.syllabuses = [
            Syllabus("CNPM-01", ["CLO1"], {"midterm": 30, "final": 40, "project": 30})
        ]

    def find_by_class_id(self, class_id):
        # Linear Search
        for syllabus in self.syllabuses:
            if syllabus.class_id == class_id:
                return syllabus
        return None
