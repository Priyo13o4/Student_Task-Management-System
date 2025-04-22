from django.db import models

class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    level = models.CharField(
        max_length=20,
        choices=[("UG", "Undergraduate"), ("PG", "Graduate")]
    )

    def __str__(self):
        return f"{self.name} ({self.code})"