# task/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.task_list, name='task_list'),
    path('detail/<int:pk>/', views.task_detail, name='task_detail'),
]