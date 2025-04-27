from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Course
from users.utils import is_admin
from .forms import CourseForm
from django.db.models import Q
from faculty.models import Faculty
from django.http import JsonResponse

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
    show_all = request.GET.get('show_all', '')
    courses = Course.objects.all()
    
    if q:
        courses = courses.filter(
            Q(name__icontains=q) |
            Q(code__icontains=q)
        )
    
    # Get total count for pagination
    total_courses = courses.count()
    
    # If not showing all and not searching, limit to 5
    if not show_all and not q:
        courses = courses[:5]
        has_more = total_courses > 5
    else:
        has_more = False

    return render(request, 'courses/course_list.html', {
        'courses': courses,
        'q': q,
        'course_form': course_form,
        'has_more': has_more,
        'show_all': show_all,
        'total_courses': total_courses,
    })

@login_required
@user_passes_test(is_admin)
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully.')
        return redirect('course_list')
    return render(request, 'courses/delete_course.html', {'course': course})

@login_required
@user_passes_test(is_admin)
def update_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully.')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('course_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': form.errors.as_json()})
            return render(request, 'courses/update_course.html', {'form': form, 'course': course})
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/update_course.html', {'form': form, 'course': course})
