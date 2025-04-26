from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('<int:task_id>/manage/', views.manage_task, name='manage_task'),
    path('<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('<int:task_id>/update-progress/', views.update_task_progress, name='update_task_progress'),
]