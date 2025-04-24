from django.contrib import messages
from .forms import TaskForm

def handle_task_creation(request):
    form = TaskForm(request.POST or None)
    if request.method == 'POST' and 'create_task' in request.POST:
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, f"Task '{task.title}' created successfully.")
            return form, True
    return form, False
