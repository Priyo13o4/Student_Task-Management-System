from django.db import models
from django.conf import settings 
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

class TaskProgress(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='student_progress')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='task_progress'
    )
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Completed', 'Completed')],
        default='Pending'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('task', 'student')

    def __str__(self):
        return f"{self.student.username} - {self.task.title} - {self.status}"

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    assigned_to = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'role': 'student'},
        related_name='assigned_tasks',
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role__in': ['faculty', 'admin']},
        related_name='created_tasks'
    )
    due_date = models.DateField(null = True)
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Completed', 'Completed')],
        default='Pending'
    )
    priority = models.CharField(
        max_length=10,
        choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')],
        null=True,
        blank=True
    )

    def get_progress_counts(self):
        # Get all assigned students
        assigned_students = self.assigned_to.all()
        
        # Create a dictionary to store counts for each status
        counts = {'Pending': 0, 'In Progress': 0, 'Completed': 0}
        
        # Count existing progress entries
        progress_counts = self.student_progress.values('status').annotate(count=models.Count('status'))
        for item in progress_counts:
            counts[item['status']] = item['count']
        
        # Add pending count for students without progress entries
        students_with_progress = self.student_progress.values_list('student_id', flat=True)
        pending_count = assigned_students.exclude(id__in=students_with_progress).count()
        counts['Pending'] += pending_count
        
        return counts

    def get_overall_status(self):
        counts = self.get_progress_counts()
        total_students = self.assigned_to.count()
        
        if counts.get('Completed', 0) == total_students and total_students > 0:
            return 'Completed'
        elif counts.get('In Progress', 0) > 0:
            return 'In Progress'
        else:
            return 'Pending'

    def __str__(self):
        return self.title