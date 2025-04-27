from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('<int:student_id>/', views.manage_student, name='manage_student'),
    path('<int:student_id>/delete/', views.delete_student, name='delete_student'),
    path('<int:student_id>/remove_course/<int:course_id>/', views.remove_course, name='remove_course'),
    path('students/', views.student_list, name='student_list'),
    path('export/csv/', views.export_grades_csv, name='export_grades_csv'),
    path('export/pdf/', views.export_grades_pdf, name='export_grades_pdf'),
    path('<int:student_id>/export/csv/', views.export_grades_csv, name='export_student_grades_csv'),
    path('<int:student_id>/export/pdf/', views.export_grades_pdf, name='export_student_grades_pdf'),
]