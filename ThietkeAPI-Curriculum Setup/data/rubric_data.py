# data/rubric_data.py
# Dữ liệu Rubric

from models.rubric import Rubric

class RubricData:
    def __init__(self):
        self.rubrics = []

    def add_rubric(self, rubric):
        self.rubrics.append(rubric)

    def get_all(self):
        return self.rubrics
