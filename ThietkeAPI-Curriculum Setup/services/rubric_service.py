# services/rubric_service.py
# Xử lý Rubric

from data.rubric_data import RubricData
from models.rubric import Rubric

class RubricService:
    def __init__(self):
        self.data = RubricData()

    def create_rubric(self, rubric_id, title, criteria):
        # API: POST /rubrics
        rubric = Rubric(rubric_id, title, criteria)
        self.data.add_rubric(rubric)
        return rubric

    def get_all_rubrics(self):
        # API: GET /rubrics
        return self.data.get_all()
