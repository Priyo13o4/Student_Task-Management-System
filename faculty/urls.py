from django.urls import path
from . import views

urlpatterns = [
    path('<int:faculty_id>/manage/', views.manage_faculty, name='manage_faculty'),
    path('api/user-email/<int:user_id>/', views.get_user_email, name='user_email'),
]