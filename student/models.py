from django.db import models

class student(models.Model) :
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=50,unique = True)
    register_no = models.CharField(max_length=12,unique = True)
    department = models.CharField(max_length=100)
    attendance = models.FloatField(default=0.0)

    def __str__(self):
        return self.name

