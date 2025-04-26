from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Course
from users.utils import is_admin
from .forms import CourseForm
from django.db.models import Q
from faculty.models import Faculty

# Create your views here.

@login_required
@user_passes_test(is_admin)
def course_list(request):
    # Handle course creation
    if request.method == 'POST' and 'create_course' in request.POST:
        course_form = CourseForm(request.POST)
        if course_form.is_valid():
            course = course_form.save()
            
            # Get the selected faculty members
            selected_faculty = course_form.cleaned_data.get('faculty', [])
            
            # Update each faculty's courses
            for faculty_user in selected_faculty:
                try:
                    faculty = Faculty.objects.get(user=faculty_user)
                    faculty.courses.add(course)
                except Faculty.DoesNotExist:
                    # If faculty profile doesn't exist, create it
                    faculty = Faculty.objects.create(user=faculty_user)
                    faculty.courses.add(course)
            
            messages.success(request, f"Course '{course.name}' created successfully.")
            return redirect('course_list')
    else:
        course_form = CourseForm()

    # Handle search
    q = request.GET.get('q', '').strip()
    courses = Course.objects.all()
    if q:
        courses = courses.filter(
            Q(name__icontains=q) |
            Q(code__icontains=q)
        )

    return render(request, 'courses/course_list.html', {
        'courses': courses,
        'q': q,
        'course_form': course_form,
    })

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
