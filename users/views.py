from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required,user_passes_test
from django.core.exceptions import PermissionDenied
from django.db import models
from django.http import JsonResponse
from student.models import Student,Course,Grade
from faculty.models import Faculty
from task.models import Task
from student.forms import StudentForm
from faculty.forms import FacultyForm
from .forms import LoginForm
from users.forms import CustomUserCreationForm
from django.contrib import messages
from student.utils import get_student_context
from .utils import is_admin, is_faculty, is_student, is_faculty_or_admin,get_admin_summary, get_faculty_context
from task.views import handle_task_creation
from users.models import CustomUser
from task.forms import TaskForm
from student.forms import GradeForm
from student.models import calculate_gpa



"""we could also use the generic http response redirect (from django.http import HttpResponse) , but its too much work"""

'''note 2 : tried Adding permission denied if someone access dashboard directly from URL from other account
It works but it redirects to login page instead of a intended 403 forbidden error , so if it works dont fix it '''

#CHanged the login view to CUstomForms in forms.py



def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            login(request, form.user)
            role = form.user.role
            if role == "admin":
                return redirect("admin_dashboard")
            elif role == "faculty":
                return redirect("faculty_dashboard")
            elif role == "student":
                return redirect("student_dashboard")

    return render(request, "users/login.html", {"form": form})

# Logout view
@login_required
def logout_view(request):
    logout(request)
    return redirect("login")

def home_redirect(request): 
    return redirect('login')

#For admin dashboard
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    if request.user.role != "admin":
        raise PermissionDenied

    summary = get_admin_summary()  # import the Summary stats

    user_form = CustomUserCreationForm(request.POST or None)   # User creation form logic

    if request.method == "POST" and 'create_user' in request.POST:
        if user_form.is_valid():
            created_user = user_form.save()
            messages.success(request, f"User '{created_user.username}' created successfully.")
            return redirect('admin_dashboard')

    if request.method == "POST" and 'create_faculty' in request.POST:
        faculty_form = FacultyForm(request.POST)
        if faculty_form.is_valid():
            faculty = faculty_form.save()
            messages.success(request, f"Faculty profile created successfully for '{faculty.user.username}'.")
            return redirect('admin_dashboard')

        

    return render(request, 'users/admin_dashboard.html', {
        **summary,
        'user_form': user_form,
    })

@login_required
@user_passes_test(is_faculty)
def faculty_dashboard(request):
    if request.user.role != "faculty" :
        raise PermissionDenied
    
    faculty = Faculty.objects.get(user=request.user)
    context = get_faculty_context(faculty)
    
    # Handle task creation using the same function as admin dashboard
    task_form, task_created, students = handle_task_creation(request)
    if task_created:
        return redirect('faculty_dashboard')
    
    context['task_form'] = task_form
    context['students'] = students
    return render(request, "users/faculty_dashboard.html", context)

@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    if request.user.role != "student":
        raise PermissionDenied
    
    # Handle task completion
    if request.method == "POST" and 'complete_task_id' in request.POST:
        task_id = request.POST.get('complete_task_id')
        try:
            task = Task.objects.get(id=task_id, assigned_to=request.user)
            task.status = "Completed"
            task.save()
            messages.success(request, f"Task '{task.title}' marked as completed.")
        except Task.DoesNotExist:
            messages.error(request, "Task not found.")
    
    context = get_student_context(request.user)
    tasks = Task.objects.filter(assigned_to=request.user)
    context['tasks'] = tasks
    context['pending_tasks'] = tasks.filter(status="Pending")
    context['completed_tasks'] = tasks.filter(status="Completed")
    return render(request, "users/student_dashboard.html", context)


@login_required
@user_passes_test(is_admin)
def faculty_list(request):
    q = request.GET.get('q', '').strip()
    faculties = Faculty.objects.all()
    if q:
        faculties = faculties.filter(
            models.Q(user__username__icontains=q) |
            models.Q(faculty_id__icontains=q)
        )
    return render(request, 'faculty/faculty_list.html', {
        'faculties': faculties,
        'q': q,
    })


@login_required
def student_grades(request):
    student = request.user.student
    grades = Grade.objects.filter(student=student)
    return render(request, 'students/student_grades.html', {
        'grades': grades,
        'gpa': student.gpa
    })

@login_required
@user_passes_test(is_admin)
def delete_course(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        try:
            course.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
@user_passes_test(is_admin)
def delete_student(request, student_id):
    if request.method == 'POST':
        student = get_object_or_404(Student, id=student_id)
        try:
            student.user.delete()  # This will also delete the student due to CASCADE
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
@user_passes_test(is_admin)
def delete_faculty(request, faculty_id):
    if request.method == 'POST':
        faculty = get_object_or_404(Faculty, id=faculty_id)
        try:
            faculty.user.delete()  # This will also delete the faculty due to CASCADE
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
@user_passes_test(is_faculty_or_admin)
def delete_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        try:
            task.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
@user_passes_test(is_faculty)
def faculty_manage_grades(request, course_id):
    if request.user.role != "faculty":
        raise PermissionDenied
    
    faculty = Faculty.objects.get(user=request.user)
    course = get_object_or_404(Course, id=course_id)
    
    # Verify that the faculty is assigned to this course
    if course not in faculty.courses.all():
        raise PermissionDenied
    
    # Get pending grades for this course
    pending_grades = Grade.objects.filter(
        course=course,
        grade__isnull=True
    ).select_related('student', 'student__user')
    
    return render(request, "users/faculty_managegradeslist.html", {
        'course': course,
        'pending_grades': pending_grades
    })

@login_required
@user_passes_test(is_faculty)
def assign_grade(request, grade_id):
    grade = get_object_or_404(Grade, id=grade_id)
    faculty = Faculty.objects.get(user=request.user)
    
    # Verify that the faculty is assigned to this course
    if grade.course not in faculty.courses.all():
        raise PermissionDenied
    
    if request.method == 'POST':
        grade_value = request.POST.get('grade')
        if not grade_value:
            return JsonResponse({'success': False, 'error': 'Grade is required'})
            
        grade.grade = grade_value
        grade.save()
        
        # Recalculate GPA
        grade.student.gpa = calculate_gpa(grade.student)
        grade.student.save(update_fields=['gpa'])
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})