# services/syllabus_service.py
# Xử lý cập nhật đề cương

from data.syllabus_data import SyllabusData

class SyllabusService:
    def __init__(self):
        self.data = SyllabusData()

    def update_syllabus(self, class_id, clos, score_weights):
        # API: PUT /syllabus/{classId}

        syllabus = self.data.find_by_class_id(class_id)

        if syllabus is None:
            return None

        # Update dữ liệu
        syllabus.clos = clos
        syllabus.score_weights = score_weights

        return syllabus
