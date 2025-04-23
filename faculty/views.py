from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from .models import Faculty
from .forms import FacultyForm
from users.utils import is_admin
from users.models import CustomUser

def get_faculty_context(user):
    faculty = Faculty.objects.get(user=user)
    courses = faculty.courses.all()

    context = {
        'faculty': faculty,
        'courses': courses,
    }

    return context

@login_required
@user_passes_test(is_admin)
def get_user_email(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    return JsonResponse({'email': user.email})

@login_required
@user_passes_test(is_admin)
def manage_faculty(request, faculty_id):
    faculty = get_object_or_404(Faculty, pk=faculty_id)
    courses = faculty.courses.all()

    # Handle course assignment
    form = FacultyForm(request.POST or None, instance=faculty)
    if request.method == 'POST' and 'submit_course' in request.POST:
        if form.is_valid():
            form.save()
            messages.success(request, f"Course assignment for {faculty.user.username} saved.")
            return redirect('manage_faculty', faculty_id=faculty_id)

    return render(request, 'users/manage_faculty.html', {
        'faculty': faculty,
        'courses': courses,
        'course_form': form,
    })
