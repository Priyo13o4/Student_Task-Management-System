from django import forms
from faculty.models import Faculty
from django.contrib.auth import get_user_model 

CustomUser = get_user_model() 
class FacultyForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role='faculty'),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': 'updateEmail();'
        }),
        required=True,
        label="Select User"
    )
    
    class Meta:
        model = Faculty
        fields = ['faculty_id', 'department', 'designation', 'email', 'phone', 'courses']
        widgets = {
            'courses': forms.CheckboxSelectMultiple(),
            'email': forms.EmailInput(attrs={
                'readonly': 'readonly',
                'class': 'form-control',
                'id': 'id_email'
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
    