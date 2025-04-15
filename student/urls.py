
from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.student_list, name='student_list'),
    path('detail/<int:pk>/', views.student_detail, name='student_detail'),
]