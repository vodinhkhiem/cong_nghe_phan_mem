# main.py
# Giả lập gọi API Curriculum Setup

from services.semester_service import SemesterService
from services.syllabus_service import SyllabusService
from services.rubric_service import RubricService

# ===== SEMESTER =====
semester_service = SemesterService()
current = semester_service.get_current_semester()

print("Current Semester:")
print("ID:", current.id)
print("Name:", current.name)
print()

# ===== SYLLABUS =====
syllabus_service = SyllabusService()
updated = syllabus_service.update_syllabus(
    "CNPM-01",
    ["CLO1", "CLO2", "CLO3"],
    {"midterm": 25, "final": 50, "project": 25}
)

print("Update syllabus success")
print("Class ID:", updated.class_id)
print("CLOs:", updated.clos)
print("Score weights:", updated.score_weights)
print()

# ===== RUBRIC =====
rubric_service = RubricService()
rubric = rubric_service.create_rubric(
    "RB001",
    "Project Evaluation",
    ["Code quality", "Documentation", "Presentation", "Teamwork"]
)

print("Create Rubric Success")
print("Rubric ID:", rubric.rubric_id)
print("Title:", rubric.title)
print("Criteria:", rubric.criteria)
print()

print("All Rubrics:")
for r in rubric_service.get_all_rubrics():
    print("-", r.title)
