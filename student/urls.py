from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('<int:student_id>/', views.manage_student, name='manage_student'),
    path('<int:student_id>/delete/', views.delete_student, name='delete_student'),
    path('<int:student_id>/remove_course/<int:course_id>/', views.remove_course, name='remove_course'),
]