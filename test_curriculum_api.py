import unittest
from services.semester_service import SemesterService
from services.syllabus_service import SyllabusService
from services.rubric_service import RubricService

class TestCurriculumAPI(unittest.TestCase):

    def setUp(self):
        self.semester_service = SemesterService()
        self.syllabus_service = SyllabusService()
        self.rubric_service = RubricService()

    def test_get_current_semester(self):
        semester = self.semester_service.get_current_semester()
        self.assertIsNotNone(semester)
        self.assertTrue(semester.is_current)

    def test_update_syllabus(self):
        result = self.syllabus_service.update_syllabus(
            "SE401",
            "Updated syllabus",
            {"Midterm": 40, "Final": 60}
        )
        self.assertTrue(result)

    def test_create_and_get_rubric(self):
        rubric = self.rubric_service.create_rubric(
            "R001",
            "Assignment Rubric",
            ["Code quality", "Documentation"]
        )
        self.assertIsNotNone(rubric)

        rubrics = self.rubric_service.get_all_rubrics()
        self.assertGreater(len(rubrics), 0)

if __name__ == "__main__":
    unittest.main()
