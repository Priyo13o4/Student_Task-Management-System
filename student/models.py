from django.db import models
from django.conf import settings  #importing custom user model here , same for task and other apps too 
from courses.models import Course

class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
            limit_choices_to={'role__in': ['student']},)
    register_no = models.CharField(max_length=12, unique=True)
    department = models.CharField(max_length=100)
    attendance = models.FloatField(default=0.0)
    courses = models.ManyToManyField(Course)
    gpa = models.FloatField(default=0.0)
    level = models.CharField(
        max_length=20,null = True ,
        choices=[("UG", "Undergraduate"), ("PG", "Graduate")])

    def __str__(self):
        return self.user.get_full_name()
    
from courses.models import Course

class Grade(models.Model):
    student = models.ForeignKey("Student", on_delete=models.CASCADE, related_name="grades")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="grades")
    grade = models.CharField(max_length=2)  # e.g., A, B, C, D, F  

    class Meta:
        unique_together = ('student', 'course')  # For one grade per student per course

    def __str__(self):
        return f"{self.student} - {self.course} : {self.grade}"
    
GRADE_POINTS = {
    "A": 10, "B": 8,"C": 6,"D": 4,"F": 0,
}

def calculate_gpa(student):
    grades = Grade.objects.filter(student=student)
    if not grades:
        return 0.0

    total_points = 0
    for g in grades:
        total_points += GRADE_POINTS.get(g.grade, 0)

    return round(total_points / grades.count(), 2) 