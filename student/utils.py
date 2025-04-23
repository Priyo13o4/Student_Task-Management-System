from student.models import Student, Grade

def get_student_context(user):
    try:
        student = Student.objects.get(user=user)
        grades = Grade.objects.filter(student=student)
        courses = student.courses.all()
        gpa = student.gpa
    except Student.DoesNotExist:
        student = None
        grades = []
        courses = []
        gpa = 0.0

    return {
        'student': student,
        'grades': grades,
        'courses': courses,
        'gpa': gpa,
    }