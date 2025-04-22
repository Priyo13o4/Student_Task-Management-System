from django.db import models
from django.conf import settings 

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'}, #u dont wanna assign it to an admin or another faculty lmao
        related_name='assigned_tasks',
        null=True, blank=True
        ) 

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role__in': ['faculty', 'admin']},
        related_name='created_tasks'
    )
    due_date = models.DateField(null = True)
    completed = models.BooleanField(default=False)
    priority = models.CharField(
        max_length=10,
        choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')]
    )

    def __str__(self):
        return self.title