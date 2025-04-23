def is_admin(user):
    return user.is_authenticated and user.role == "admin"

def is_faculty(user):
    return user.is_authenticated and user.role == "faculty"

def is_student(user):
    return user.is_authenticated and user.role == "student"

def is_faculty_or_admin(user):
    return user.is_authenticated and user.role in ["faculty", "admin"]

def get_admin_summary():
    from student.models import Student, Course, Grade
    from faculty.models import Faculty
    from task.models import Task

    return {
        'total_students': Student.objects.count(),
        'total_faculty': Faculty.objects.count(),
        'total_tasks': Task.objects.count(),
        'total_courses': Course.objects.count(),
    }
