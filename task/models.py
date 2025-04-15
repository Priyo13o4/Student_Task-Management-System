from django.db import models
from student.models import Student
from users.models import CustomUser

class Task(models.Model):
    PRIORITY_CHOICES = [('Low', 'Low'), ('Med', 'Medium'), ('High', 'High')]
    title = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateTimeField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    assigned_to_student = models.ForeignKey(Student, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    assigned_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_tasks')

    def __str__(self):
        return self.title