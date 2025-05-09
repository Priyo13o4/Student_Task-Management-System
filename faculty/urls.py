from django.urls import path
from . import views

urlpatterns = [
    path('<int:faculty_id>/manage/', views.manage_faculty, name='manage_faculty'),
    path('api/user-email/<int:user_id>/', views.get_user_email, name='user_email'),
    path('delete/<int:faculty_id>/', views.delete_faculty, name='delete_faculty'),
    path('faculty_list/', views.faculty_list, name='faculty_list'),
    path('remove-course/<int:faculty_id>/<int:course_id>/', views.remove_course, name='remove_course'),
    path('manage-tasks/', views.manage_faculty_tasks, name='manage_faculty_tasks'),
    path('manage-tasks/<int:task_id>/delete/', views.delete_faculty_task, name='delete_faculty_task'),
]