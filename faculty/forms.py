from django import forms
from faculty.models import Faculty
from django.contrib.auth import get_user_model 
from courses.models import Course

CustomUser = get_user_model()

class CourseAssignmentForm(forms.ModelForm):
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=forms.Select(attrs={
            'class': 'select2',
            'data-placeholder': 'Search and select a course...',
            'style': 'width: 100%;'
        }),
        required=True,
        label="Select Course"
    )

    class Meta:
        model = Faculty
        fields = ['course']

    def save(self, commit=True):
        instance = super().save(commit=False)
        course = self.cleaned_data.get('course')
        if course:
            instance.courses.add(course)
        if commit:
            instance.save()
        return instance

class FacultyForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role='faculty'),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': 'updateEmail();'
        }),
        required=True,
        label="Select Faculty User"
    )
    
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'select2',
            'data-placeholder': 'Search and select courses...',
            'style': 'width: 100%;'
        }),
        required=False,
        label="Select Courses"
    )
    
    class Meta:
        model = Faculty
        fields = ['user', 'faculty_id', 'department', 'designation', 'email', 'phone', 'courses']
        widgets = {
            'email': forms.EmailInput(attrs={
                'readonly': 'readonly',
                'class': 'form-control',
                'id': 'id_email'
            }),
            'faculty_id': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 100,
                'max': 999
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get the last faculty ID and increment it
        last_faculty = Faculty.objects.order_by('-faculty_id').first()
        if last_faculty:
            self.initial['faculty_id'] = last_faculty.faculty_id + 1
        else:
            self.initial['faculty_id'] = 100  # Start with 100 if no faculty exists
            
        # If we're editing an existing faculty, hide the user field
        if self.instance and self.instance.pk:
            self.fields['user'].widget = forms.HiddenInput()
            self.fields['user'].required = False
            
        # Filter out users who already have faculty profiles
        self.fields['user'].queryset = CustomUser.objects.filter(
            role='faculty'
        ).exclude(
            faculty__isnull=False
        )
        
    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        if user:
            cleaned_data['email'] = user.email
        return cleaned_data
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.user:
            instance.email = instance.user.email
        if commit:
            instance.save()
            # Save the many-to-many relationship
            self.save_m2m()
        return instance
    