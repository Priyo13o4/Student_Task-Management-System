from django import forms
from student.models import Grade, GRADE_POINTS,Student
from courses.models import Course
from django.contrib.auth import get_user_model 
#the other method of importing settings from django.config is only for models.py


CustomUser = get_user_model()
class CourseAssignmentForm(forms.ModelForm):
    course = forms.ModelChoiceField(
        queryset=Course.objects.none(),  # Will be set in __init__
        widget=forms.Select(attrs={
            'class': 'select2',
            'data-placeholder': 'Search and select a course...',
            'style': 'width: 100%;'
        }),
        required=True
    )

    class Meta:
        model = Student
        fields = ['course']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            # Filter courses by student's level and exclude already assigned courses
            self.fields['course'].queryset = Course.objects.filter(
                level=self.instance.level
            ).exclude(
                id__in=self.instance.courses.values_list('id', flat=True)
            )

class StudentForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role='student').exclude(student__isnull=False),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Select a student user'
        }),
        required=True,
        label="Student User *"
    )
    
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'select2',
            'data-placeholder': 'Search and select courses...',
            'style': 'width: 100%;'
        }),
        required=False,
        label="Courses"
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
            'register_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter registration number (ex : 20231CAI0149)'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter department name'
            }),
            
            'level': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select student level'
            }),
        }
        labels = {
            'register_no': 'Registration Number *',
            'department': 'Department',
            'attendance': 'Attendance',
            'level': 'Level *'
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

    def __init__(self, *args, student=None, **kwargs):
        super().__init__(*args, **kwargs)
        if student:
            self.fields['student'].initial = student.id
            self.fields['student'].widget = forms.HiddenInput()
            # Only show courses for this student
            self.fields['course'].queryset = student.courses.all()
            
            # If we're editing an existing grade, set the initial values
            if self.instance and self.instance.pk:
                self.fields['course'].initial = self.instance.course
                self.fields['grade'].initial = self.instance.grade

    def save(self, commit=True):
        if not self.instance.pk:  # If this is a new grade
            try:
                # Try to get existing grade
                existing_grade = Grade.objects.get(
                    student=self.cleaned_data['student'],
                    course=self.cleaned_data['course']
                )
                # Update the existing grade
                existing_grade.grade = self.cleaned_data['grade']
                if commit:
                    existing_grade.save()
                return existing_grade
            except Grade.DoesNotExist:
                # If no existing grade, create new one
                return super().save(commit)
        else:
            # If we're updating an existing grade
            return super().save(commit)
