from django.db import models
from django.conf import settings  
from django.core.exceptions import ValidationError
from courses.models import Course

def validate_three_digit(value):
    if value < 100 or value > 999:
        raise ValidationError('Faculty ID must be a 3-digit number.')
    
class Faculty(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
    limit_choices_to={'role__in': ['faculty']},) #again you dont want a student to be a faculty lol
    faculty_id = models.IntegerField(blank= True,null=True,unique=True,validators=[validate_three_digit])
    department = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=100, blank = True)
    phone_no = models.CharField(max_length = 15 ,null = True)
    courses = models.ManyToManyField(Course)


    def __str__(self):
        return self.user.username
    class Meta:
        verbose_name_plural = "Faculty" 