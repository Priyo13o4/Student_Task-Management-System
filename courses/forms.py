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
                'placeholder': 'Enter course code (ex MAT2001)'
            }),
        }
        labels = {
            'name': 'Course Name *',
            'code': 'Course Code *',
        }

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if self.instance and self.instance.pk:
            # If we're updating an existing course, exclude it from the check
            if Course.objects.filter(code=code).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Course code already exists")
        else:
            # If we're creating a new course
            if Course.objects.filter(code=code).exists():
                raise forms.ValidationError("Course code already exists")
        return code
