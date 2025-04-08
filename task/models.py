from django.db import models
from student.models import student

class task(models.Model) :

    title = models.CharField(max_length= 200)
    description = models.TextField()
    deadline = models.DateTimeField()
    priority = models.CharField(max_length=10,choices=[('Low','Low'),('Med','Medium'),('High','High')])
    assigned_to_student = models.ForeignKey(student,on_delete= models.CASCADE)
    completed = models.BooleanField(default = False)

    def __str__(self):
        return self.title

