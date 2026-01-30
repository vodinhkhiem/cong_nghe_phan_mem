# models/rubric.py
# Mô hình Rubric (tiêu chí chấm điểm)

class Rubric:
    def __init__(self, rubric_id, title, criteria):
        self.rubric_id = rubric_id
        self.title = title
        self.criteria = criteria
