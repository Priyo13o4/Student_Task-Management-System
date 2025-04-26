from django import forms
from django.contrib.auth import get_user_model
from task.models import Task

CustomUser = get_user_model()

class TaskForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter task title (ex: Complete Assignment 1)'
        }),
        required=True,
        label="Title *"
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Enter detailed task description'
        }),
        required=True,
        label="Description *"
    )
    
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        required=True,
        label="Due Date *"
    )
    
    assigned_to = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.filter(role='student'),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2',
            'data-placeholder': 'Search and select students...',
            'style': 'width: 100%;'
        }),
        required=True,
        label="Assign To *"
    )
    
    priority = forms.ChoiceField(
        choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')],
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        initial='Medium',
        required=True,
        label="Priority *"
    )
    
    status = forms.CharField(
        widget=forms.HiddenInput(),
        initial='Pending',
        required=False
    )

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "assigned_to",
            "due_date",
            "status",
            "priority"
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Filter users to only show students
        self.fields['assigned_to'].queryset = CustomUser.objects.filter(role='student')
        # Set initial status to Pending
        self.fields['status'].initial = 'Pending'
        # Set initial priority to Medium
        self.fields['priority'].initial = 'Medium'

    def save(self, commit=True):
        task = super().save(commit=False)
        if self.user:
            task.created_by = self.user
        if commit:
            task.save()
            self.save_m2m()
        return task