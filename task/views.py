from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from .forms import TaskForm
from .models import Task, TaskProgress
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db import models
from users.utils import is_faculty_or_admin, is_student
from django.http import JsonResponse
import json

@login_required
@user_passes_test(is_faculty_or_admin)
def task_list(request):
    q = request.GET.get('q', '').strip()
    tasks = Task.objects.all()
    if q:
        tasks = tasks.filter(
            models.Q(title__icontains=q) |
            models.Q(description__icontains=q)
        )
    
    # Handle task creation
    task_form, task_created, students = handle_task_creation(request)
    if task_created:
        return redirect('task_list')

    return render(request, 'tasks/task_list.html', {
        'tasks': tasks,
        'q': q,
        'task_form': task_form,
        'students': students
    })


CustomUser = get_user_model()

def handle_task_creation(request):
    form = TaskForm(request.POST or None, user=request.user)
    students = CustomUser.objects.filter(role='student')
    
    if request.method == 'POST' and 'create_task' in request.POST:
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, f"Task '{task.title}' created successfully.")
            return form, True, students
    return form, False, students

def manage_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    students = CustomUser.objects.filter(role='student')
    
    if request.method == 'POST':
        if 'delete_task' in request.POST:
            task.delete()
            messages.success(request, f"Task '{task.title}' deleted successfully.")
            return redirect('task_list')
        elif 'update_task' in request.POST:
            form = TaskForm(request.POST, instance=task, user=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, f"Task '{task.title}' updated successfully.")
                return redirect('task_list')
    else:
        form = TaskForm(instance=task, user=request.user)
    
    return render(request, 'tasks/manage_task.html', {
        'task': task,
        'form': form,
        'students': students
    })

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
@user_passes_test(is_student)
def update_task_progress(request, task_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            status = data.get('status')
            
            if status not in ['Pending', 'In Progress', 'Completed']:
                return JsonResponse({'success': False, 'error': 'Invalid status'})
            
            task = get_object_or_404(Task, id=task_id)
            
            # Get or create task progress for this student
            task_progress, created = TaskProgress.objects.get_or_create(
                task=task,
                student=request.user,
                defaults={'status': status}
            )
            
            if not created:
                task_progress.status = status
                task_progress.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Task status updated to {status}'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
   



