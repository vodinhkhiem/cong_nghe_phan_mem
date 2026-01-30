# models/syllabus.py
# Mô hình đề cương môn học

class Syllabus:
    def __init__(self, class_id, clos, score_weights):
        self.class_id = class_id
        self.clos = clos
        self.score_weights = score_weights
