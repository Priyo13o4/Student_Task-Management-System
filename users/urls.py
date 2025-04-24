from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("faculty-dashboard/", views.faculty_dashboard, name="faculty_dashboard"),
    path("student-dashboard/", views.student_dashboard, name="student_dashboard"),
    path('students/', views.student_list, name='student_list'),
    path('faculty/', views.faculty_list, name='faculty_list'),
    path('tasks/', views.task_list, name='task_list'),
]