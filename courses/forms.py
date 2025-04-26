from django import forms
from courses.models import Course
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class CourseForm(forms.ModelForm):
    faculty = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.filter(role='faculty'),
        widget=forms.SelectMultiple(attrs={
            'class': 'select2',
            'data-placeholder': 'Search and select faculty...',
            'style': 'width: 100%;'
        }),
        required=False,
        label="Faculty"
    )

    level = forms.ChoiceField(
        choices=[("UG", "Undergraduate(UG)"), ("PG", "Postgraduate(PG)")],
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        required=True,
        label="Level *"
    )

    class Meta:
        model = Course
        fields = ['name', 'code', 'level', 'faculty']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter course name (ex : Transform Mathematics)'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter course code (ex MAT200)'
            }),
        }
        labels = {
            'name': 'Course Name *',
            'code': 'Course Code *',
        }
