from django.db import models
from django.conf import settings

class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    level = models.CharField(
        max_length=20,
        choices=[("UG", "Undergraduate(UG)"), ("PG", "Postgraduate(PG)")]
    )
    faculty = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'role': 'faculty'},
        related_name='teaching_courses',
        blank=True
    )

    def __str__(self):
        return f"{self.name} ({self.code})"