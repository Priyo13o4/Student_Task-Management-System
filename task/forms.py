from django import forms
from django.contrib.auth import get_user_model
from task.models import Task

CustomUser = get_user_model()

class TaskForm(forms.ModelForm):
    assign_to_all = forms.BooleanField(
        required=False,
        label='Assign to all students',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "assigned_to",
            "created_by",
            "due_date",
            "status",
            "priority",
            "assign_to_all"
        ]
        widgets = {
            "due_date": forms.DateInput(attrs={'type': 'date'}),
            "description": forms.Textarea(attrs={'rows': 4}),
            "assigned_to": forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter assigned_to to students
        self.fields['assigned_to'].queryset = CustomUser.objects.filter(role='student')
        # Filter created_by to faculty or admin
        self.fields['created_by'].queryset = CustomUser.objects.filter(role__in=['faculty', 'admin'])
        # Reorder fields to put assign_to_all after assigned_to
        self.fields['assign_to_all'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['assign_to_all'].label = 'Assign to all students'
        self.fields['assign_to_all'].help_text = 'Check this to assign the task to all students'

    def clean(self):
        cleaned_data = super().clean()
        assign_to_all = cleaned_data.get('assign_to_all')
        assigned_to = cleaned_data.get('assigned_to')

        if assign_to_all and assigned_to:
            # If assign_to_all is checked, assign to all students
            cleaned_data['assigned_to'] = CustomUser.objects.filter(role='student')
        elif not assign_to_all and not assigned_to:
            raise forms.ValidationError("Please select at least one student or check 'Assign to all students'")

        return cleaned_data