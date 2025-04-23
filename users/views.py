from django.shortcuts import redirect, render
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required,user_passes_test
from django.core.exceptions import PermissionDenied
from django.db import models
from student.models import Student,Course,Grade
from faculty.models import Faculty
from task.models import Task
from student.forms import StudentForm
from faculty.forms import FacultyForm
from .forms import LoginForm
from users.forms import CustomUserCreationForm
from django.contrib import messages
from student.utils import get_student_context
from .utils import is_admin, is_faculty, is_student, is_faculty_or_admin,get_admin_summary
from task.views import handle_task_creation


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
            request.session['new_user_id'] = created_user.id
            return redirect('admin_dashboard')
        
    if request.method == "POST" and 'create_student' in request.POST:
        student_form = StudentForm(request.POST)
        if student_form.is_valid():
                student = student_form.save()
                student.save()
                messages.success(request, f"Student '{student.user.username}' created successfully.")
                return redirect('admin_dashboard')

    if request.method == "POST" and 'create_faculty' in request.POST:
        faculty_form = StudentForm(request.POST)
        if faculty_form.is_valid():
                faculty = faculty_form.save(commit=False)
                faculty.user_id = request.session.pop('new_user_id', None)
                faculty.save()
                messages.success(request, f"Faculty '{faculty.user.username}' created successfully.")
                return redirect('admin_dashboard')
    
    task_form, task_created = handle_task_creation(request)
    if task_created:
        return redirect('admin_dashboard')

    return render(request, 'users/admin_dashboard.html', {
        **summary ,
        'user_form': user_form,
        'student_form': StudentForm(),
        'faculty_form' : FacultyForm(),
        'task_form': task_form
    })

@login_required
@user_passes_test(is_faculty)
def faculty_dashboard(request):
    if request.user.role != "faculty" :
        raise PermissionDenied
    return render(request, "users/faculty_dashboard.html")

@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    if request.user.role != "student" :
        raise PermissionDenied
    context = get_student_context(request.user)
    return render(request, "users/student_dashboard.html", context)

@login_required
@user_passes_test(is_faculty_or_admin)
def student_list(request):
    q = request.GET.get('q', '').strip()
    students = Student.objects.all()
    if q:
        students = students.filter(
            models.Q(user__username__icontains=q) |
            models.Q(register_no__icontains=q)
        )
    return render(request, 'students/student_list.html', {
        'students': students,
        'q': q,
    })

@login_required
@user_passes_test(is_faculty_or_admin)
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})

@login_required
def student_grades(request):
    student = request.user.student
    grades = Grade.objects.filter(student=student)
    return render(request, 'students/student_grades.html', {
        'grades': grades,
        'gpa': student.gpa
    })