from student.models import Student, Grade
from courses.models import Course

def get_student_context(user):
    student = Student.objects.get(user=user)
    grades = Grade.objects.filter(student=student)
    courses = student.courses.all()

    GRADE_POINTS = {"A": 10, "B": 8, "C": 6, "D": 4, "F": 0}
    gpa = 0.0
    if grades.exists():
        total = sum(GRADE_POINTS.get(g.grade, 0) for g in grades)
        gpa = round(total / grades.count(), 2)

    context = {
        'student': student,
        'grades': grades,
        'courses': courses,
        'gpa': gpa
    }

    # return {
    #     'student': student,
    #     'grades': grades,
    #     'courses': courses,
    #     'gpa': gpa,
    # }