from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from faculty.models import Faculty

User = get_user_model()

@receiver(post_delete, sender=Faculty)
def delete_user_on_faculty_delete(sender, instance, **kwargs):
    """
    Delete the user when their faculty/student profile is deleted
    """
    try:
        user = instance.user
        if user and user.role == 'faculty':
            user.delete()
    except User.DoesNotExist:
        pass 