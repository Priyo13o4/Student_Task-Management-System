from django.db import models
from django.conf import settings

class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    level = models.CharField(
        max_length=20,
        choices=[("UG", "Undergraduate"), ("PG", "Graduate")]
    )
    faculty = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'faculty'},
        related_name='teaching_courses'
    )

    def __str__(self):
        return f"{self.name} ({self.code})"