from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from .models import Faculty
from .forms import CourseAssignmentForm, FacultyForm
from users.utils import is_admin, is_faculty_or_admin
from users.models import CustomUser
from django.db import models
from django.db.models import Q
from courses.models import Course
from task.models import Task
from task.forms import TaskForm

def get_faculty_context(user):
    faculty = Faculty.objects.get(user=user)
    courses = faculty.courses.all()

    context = {
        'faculty': faculty,
        'courses': courses,
    }

    return context

@login_required
@user_passes_test(is_admin)
def get_user_email(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    return JsonResponse({'email': user.email})

@login_required
@user_passes_test(is_admin)
def faculty_list(request):
    q = request.GET.get('q', '').strip()
    show_all = request.GET.get('show_all', '')
    
    # Base queryset with ordering
    faculties = Faculty.objects.all().order_by('user__username')
    
    # Apply search if query exists
    if q:
        faculties = faculties.filter(
            Q(user__username__icontains=q) |
            Q(faculty_id__icontains=q) |
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q)
        )

    total_faculties = faculties.count()

    if not show_all and not q:
        faculties = faculties[:5]
        has_more = total_faculties > 5
    else:
        has_more = False

    if request.method == 'POST' and 'create_faculty' in request.POST:
        form = FacultyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Faculty created successfully.')
            return redirect('faculty_list')
    else:
        form = FacultyForm()

    return render(request, 'faculty/faculty_list.html', {
        'faculties': faculties,
        'q': q,
        'total_faculties': total_faculties,
        'has_more': has_more,
        'faculty_form': form,
    })

@login_required
@user_passes_test(is_admin)
def manage_faculty(request, faculty_id):
    faculty = get_object_or_404(Faculty, pk=faculty_id)
    courses = faculty.courses.all()

    # Handle course assignment
    course_form = CourseAssignmentForm(request.POST or None, instance=faculty)
    if request.method == 'POST':
        if 'submit_course' in request.POST:
            if course_form.is_valid():
                course_form.save()
                messages.success(request, f"Course assigned to {faculty.user.username} successfully.")
                return redirect('manage_faculty', faculty_id=faculty_id)
        elif 'update_details' in request.POST:
            # Update user information
            faculty.user.first_name = request.POST.get('first_name', '')
            faculty.user.last_name = request.POST.get('last_name', '')
            faculty.user.save()
            
            # Update faculty information
            faculty.department = request.POST.get('department', '')
            faculty.designation = request.POST.get('designation', '')
            faculty.email = request.POST.get('email', '')
            faculty.phone = request.POST.get('phone', '')
            faculty.save()
            
            messages.success(request, f"Details for {faculty.user.username} have been updated.")
            return redirect('manage_faculty', faculty_id=faculty_id)

    return render(request, 'faculty/manage_faculty.html', {
        'faculty': faculty,
        'courses': courses,
        'course_form': course_form,
    })

@login_required
@user_passes_test(is_admin)
def delete_faculty(request, faculty_id):
    if request.method == 'POST':
        faculty = get_object_or_404(Faculty, id=faculty_id)
        try:
            # Store the user instance and delete it first
            user = faculty.user
            if user and user.role == 'faculty':
                user.delete()
            else:
                # If user doesn't exist or isn't a faculty member, just delete the faculty profile
                faculty.delete()
                
            return JsonResponse({
                'success': True,
                'message': 'Faculty member deleted successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

@login_required
@user_passes_test(is_admin)
def remove_course(request, faculty_id, course_id):
    faculty = get_object_or_404(Faculty, pk=faculty_id)
    course = get_object_or_404(Course, pk=course_id)
    
    try:
        faculty.courses.remove(course)
        return JsonResponse({
            'success': True,
            'message': f'Course {course.name} has been removed from {faculty.user.username}'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@user_passes_test(is_faculty_or_admin)
def manage_faculty_tasks(request):
    faculty = Faculty.objects.get(user=request.user)
    courses = faculty.courses.all()
    
    # Get tasks created by this faculty member, ordered by due date
    tasks = Task.objects.filter(created_by=request.user).order_by('due_date')
    
    # Handle task creation
    if request.method == 'POST':
        if 'create_task' in request.POST:
            form = TaskForm(request.POST, user=request.user)
            if form.is_valid():
                task = form.save(commit=False)
                task.created_by = request.user
                task.save()
                form.save_m2m()  # Save many-to-many relationships
                messages.success(request, f"Task '{task.title}' created successfully.")
                return redirect('manage_faculty_tasks')
        elif 'update_task' in request.POST:
            task_id = request.POST.get('task_id')
            task = get_object_or_404(Task, id=task_id)
            form = TaskForm(request.POST, instance=task, user=request.user)
            if form.is_valid():
                task = form.save(commit=False)
                task.save()
                form.save_m2m()  # Save many-to-many relationships
                messages.success(request, f"Task '{task.title}' updated successfully.")
                return redirect('manage_faculty_tasks')
    else:
        form = TaskForm(user=request.user)
    
    return render(request, 'users/faculty_managetasks.html', {
        'faculty': faculty,
        'courses': courses,
        'tasks': tasks,
        'form': form,
    })

@login_required
@user_passes_test(is_faculty_or_admin)
def delete_faculty_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        try:
            task.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
