
from django.urls import path
from . import views

urlpatterns = [
    path('<int:student_id>/manage/', views.manage_student, name='manage_student'),
]