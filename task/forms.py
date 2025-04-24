from django import forms
from django.contrib.auth import get_user_model
from task.models import Task

CustomUser = get_user_model()

class TaskForm(forms.ModelForm):
    assign_to_all = forms.BooleanField(
        required=False,
        label='Assign to all students',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'onchange': 'toggleStudentSelection()'})
    )

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "assigned_to",
            "due_date",
            "status",
            "priority",
            "assign_to_all"
        ]
        widgets = {
            "due_date": forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            "description": forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            "assigned_to": forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            "title": forms.TextInput(attrs={'class': 'form-control'}),
            "priority": forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter assigned_to to students
        self.fields['assigned_to'].queryset = CustomUser.objects.filter(role='student')
        # Set initial status to Pending
        self.fields['status'].initial = 'Pending'
        self.fields['status'].widget = forms.HiddenInput()
        # Set initial priority to Medium
        self.fields['priority'].initial = 'Medium'

    def clean(self):
        cleaned_data = super().clean()
        assign_to_all = cleaned_data.get('assign_to_all')
        assigned_to = cleaned_data.get('assigned_to')

        if assign_to_all:
            # If assign_to_all is checked, assign to all students
            cleaned_data['assigned_to'] = CustomUser.objects.filter(role='student')
        elif not assigned_to:
            raise forms.ValidationError("Please select at least one student or check 'Assign to all students'")

        return cleaned_data

    def save(self, commit=True):
        task = super().save(commit=False)
        if commit:
            task.save()
            self.save_m2m()
        return task