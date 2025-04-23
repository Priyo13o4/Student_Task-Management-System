from django import forms
from django.contrib.auth import get_user_model
from task.models import Task

CustomUser = get_user_model()

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "assigned_to",
            "created_by",
            "due_date",
            "completed",
            "priority"
        ]
        widgets = {
            "due_date": forms.DateInput(attrs={'type': 'date'}),
            "description": forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter assigned_to to students
        self.fields['assigned_to'].queryset = CustomUser.objects.filter(role='student')
        # Filter created_by to faculty or admin
        self.fields['created_by'].queryset = CustomUser.objects.filter(role__in=['faculty', 'admin'])