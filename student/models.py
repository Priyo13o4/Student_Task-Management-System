from django.db import models
from users.models import CustomUser  #importing custom user model here , same for task app too 

class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    register_no = models.CharField(max_length=12, unique=True)
    department = models.CharField(max_length=100)
    attendance = models.FloatField(default=0.0)

    def __str__(self):
        return self.user.get_full_name()