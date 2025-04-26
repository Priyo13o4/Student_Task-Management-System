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
        label="Assign Faculty"
    )

    class Meta:
        model = Course
        fields = ['name', 'code', 'level', 'faculty']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'level': forms.Select(attrs={'class': 'form-control'}),
        }
