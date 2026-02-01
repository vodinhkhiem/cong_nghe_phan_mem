from services.semester_service import SemesterService
from services.syllabus_service import SyllabusService
from services.rubric_service import RubricService

semester_service = SemesterService()
syllabus_service = SyllabusService()
rubric_service = RubricService()

print("=== GET CURRENT SEMESTER ===")
semester = semester_service.get_current_semester()
print(f"Semester: {semester.name}")

print("\n=== UPDATE SYLLABUS ===")
syllabus_service.update_syllabus(
    "SE401",
    "Updated syllabus for Software Engineering",
    {
        "Midterm": 30,
        "Final": 50,
        "Assignment": 20
    }
)

print("Class: SE401")
print("Status: Updated successfully")

print("\n=== CREATE RUBRIC ===")
rubric = rubric_service.create_rubric(
    "R001",
    "Assignment Rubric",
    ["Code quality", "Documentation", "Presentation"]
)
print("Rubric created:")
print("-", rubric.title)

print("\n=== GET ALL RUBRICS ===")
for r in rubric_service.get_all_rubrics():
    print("-", r.title)
