from django.contrib import messages
from .forms import TaskForm

def handle_task_creation(request):
    form = TaskForm(request.POST or None)
    if request.method == 'POST' and 'create_task' in request.POST:
        if form.is_valid():
            task = form.save()
            messages.success(request, f"Task “{task.title}” created.")
            return form, True
    return form, False
