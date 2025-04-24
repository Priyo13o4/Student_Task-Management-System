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

def get_faculty_context(faculty):
    from student.models import Student, Course, Grade
    from task.models import Task
    from faculty.models import Faculty

    # Get faculty's courses
    faculty_courses = Course.objects.filter(faculty=faculty.user)
    
    # Get students enrolled in faculty's courses
    enrolled_students = Student.objects.filter(courses__in=faculty_courses).distinct()
    
    # Get tasks created by faculty using faculty.user
    faculty_tasks = Task.objects.filter(created_by=faculty.user)
    
    # Get pending grades (grades that need to be assigned)
    pending_grades = Grade.objects.filter(
        course__in=faculty_courses,
        grade__isnull=True
    )

    # Get recent tasks ordered by due_date
    recent_tasks = faculty_tasks.order_by('-due_date')[:5]

    # Get list of pending grades with student and course info
    pending_grades_list = pending_grades.select_related('student', 'course')

    return {
        'faculty': faculty,
        'courses': faculty_courses,
        'students': enrolled_students,
        'tasks': faculty_tasks,
        'pending_grades': pending_grades.count(),
        'pending_grades_list': pending_grades_list,
        'recent_tasks': recent_tasks,
        'faculty_name': f"{faculty.user.first_name} {faculty.user.last_name}"
    }
