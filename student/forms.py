from django import forms
from student.models import Grade, GRADE_POINTS,Student
from courses.models import Course
from django.contrib.auth import get_user_model 
#the other method of importing settings from django.config is only for models.py


CustomUser = get_user_model()

class StudentForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role='student'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        label="Select User"
    )

    class Meta:
        model = Student
        fields = [
            'user',
            'register_no',
            'department',
            'attendance',
            'courses',
            'level', 
        ]
        widgets = {
            'courses': forms.CheckboxSelectMultiple(),  # optional can be dropdown also
            'level': forms.Select(attrs={'class': 'form-control'}),
        }

GRADE_CHOICES = [
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'C'),
    ('D', 'D'),
    ('F', 'F'),
]

class GradeForm(forms.ModelForm):
    grade = forms.ChoiceField(choices=GRADE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Grade
        fields = ['student', 'course', 'grade']
        widgets = {
            'student': forms.HiddenInput(),  # Hide this field and set it in the view
            'course': forms.Select(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        grade_obj = super().save(commit=False)
        if commit:
            grade_obj.save()
        return grade_obj

    def __init__(self, *args, student=None, **kwargs):
        super().__init__(*args, **kwargs)
        if student:
            self.fields['student'].initial = student.id
            self.fields['student'].widget = forms.HiddenInput()
            # Only show courses for this student
            self.fields['course'].queryset = student.courses.all()
