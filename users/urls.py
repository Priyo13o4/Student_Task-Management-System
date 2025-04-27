from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_redirect),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('faculty/dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('students/<int:student_id>/delete/', views.delete_student, name='delete_student'),
    path('faculty/<int:faculty_id>/delete/', views.delete_faculty, name='delete_faculty'),
    path('courses/<int:course_id>/delete/', views.delete_course, name='delete_course'),
    path('student/grades/', views.student_grades, name='student_grades'),
]