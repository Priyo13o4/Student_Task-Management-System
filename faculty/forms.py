from django import forms
from faculty.models import Faculty
from django.contrib.auth import get_user_model 

CustomUser = get_user_model() 
class FacultyForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role='faculty'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        label="Select User"
    )
    
    class Meta:
        model = Faculty
        fields = ['faculty_id','department', 'designation','email','phone_no','courses']

        widgets = {
            'courses': forms.CheckboxSelectMultiple()}
    