from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Course
from users.utils import is_admin

# Create your views here.

@login_required
@user_passes_test(is_admin)
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})

@login_required
@user_passes_test(is_admin)
def delete_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        course_name = course.name
        course.delete()
        messages.success(request, f"Course '{course_name}' has been deleted.")
        return redirect('course_list')
    return render(request, 'courses/confirm_delete.html', {'course': course})
