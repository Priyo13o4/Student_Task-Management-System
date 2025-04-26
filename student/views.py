from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CourseAssignmentForm
from django.contrib import messages
from django.db.models import Q
from .models import Student, calculate_gpa, Grade, Course
from .forms import GradeForm, StudentForm
from users.utils import is_faculty_or_admin, is_admin
from task.models import Task
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from courses.forms import CourseForm




@login_required
@user_passes_test(is_faculty_or_admin)
def student_list(request):
    search_query = request.GET.get('q', '')
    show_all = request.GET.get('show_all', '')
    
    # Base queryset with ordering
    students = Student.objects.all().order_by('user__username')
    
    # Apply search if query exists
    if search_query:
        students = students.filter(
            Q(user__username__icontains=search_query) |
            Q(register_no__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query)
        )
    
    # Get total count for pagination
    total_students = students.count()
    
    # If not showing all and not searching, limit to 5
    if not show_all and not search_query:
        students = students[:5]
        has_more = total_students > 5
    else:
        has_more = False

    # Handle student creation
    if request.method == 'POST' and 'create_student' in request.POST:
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student created successfully.')
            return redirect('student_list')
    else:
        form = StudentForm()

    return render(request, 'students/student_list.html', {
        'students': students,
        'q': search_query,
        'has_more': has_more,
        'total_students': total_students,
        'show_all': show_all,
        'student_form': form
    })

@login_required
@user_passes_test(is_faculty_or_admin)
def manage_student(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    grades = student.grades.all()
    courses = student.courses.all()
    gpa = calculate_gpa(student)

    # Handle student details update
    if request.method == 'POST' and 'update_details' in request.POST:
        # Update user information
        student.user.first_name = request.POST.get('first_name', '')
        student.user.last_name = request.POST.get('last_name', '')
        student.user.save()
        
        # Update student information
        student.register_no = request.POST.get('register_no', '')
        student.department = request.POST.get('department', '')
        
        # Validate and set level
        level = request.POST.get('level', '')
        if level in ['UG', 'PG']:
            student.level = level
        else:
            messages.error(request, "Invalid level. Must be either UG or PG.")
            return redirect('manage_student', student_id=student_id)
            
        student.save()
        messages.success(request, f"Details for {student.user.username} have been updated.")
        return redirect('manage_student', student_id=student_id)

    # Handle course assignment
    if request.method == 'POST' and 'submit_course' in request.POST:
        course_form = CourseAssignmentForm(request.POST, instance=student)
        if course_form.is_valid():
            course = course_form.cleaned_data['course']
            # Double check that the course level matches the student's level
            if course.level != student.level:
                messages.error(request, f"Cannot assign {course.level} course to {student.level} student.")
                return redirect('manage_student', student_id=student_id)
            
            student.courses.add(course)  # Add the course to student's courses
            messages.success(request, f"Course '{course.name}' assigned to {student.user.username} successfully.")
            return redirect('manage_student', student_id=student_id)
        else:
            messages.error(request, "Invalid course selection.")
    else:
        course_form = CourseAssignmentForm(instance=student)

    # Handle grade assignment
    if request.method == 'POST' and 'submit_grade' in request.POST:
        course_id = request.POST.get('course')
        try:
            # Try to get existing grade
            existing_grade = Grade.objects.get(student=student, course_id=course_id)
            form = GradeForm(request.POST, instance=existing_grade, student=student)
        except Grade.DoesNotExist:
            # If no existing grade, create new form
            form = GradeForm(request.POST, student=student)
        
        if form.is_valid():
            try:
                grade = form.save()
                # Recalculate GPA
                student.gpa = calculate_gpa(student)
                student.save(update_fields=['gpa'])
                messages.success(request, f"Grade for {student.user.username} saved.")
                return redirect('manage_student', student_id=student_id)
            except Exception as e:
                messages.error(request, f"Error saving grade: {str(e)}")
                return redirect('manage_student', student_id=student_id)
    else:
        form = GradeForm(student=student)

    return render(request, 'students/manage_student.html', {
        'student': student,
        'grades':  grades,
        'courses': courses,
        'gpa':     gpa,
        'grade_form': form,
        'course_form': course_form,
    })

@login_required
@user_passes_test(is_admin)
def delete_student(request, student_id):
    if request.method == 'POST':
        student = get_object_or_404(Student, id=student_id)
        try:
            student.user.delete()  # This will also delete the student due to CASCADE
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
@user_passes_test(is_faculty_or_admin)
@require_POST
@csrf_exempt
def remove_course(request, student_id, course_id):
    try:
        student = Student.objects.get(id=student_id)
        course = Course.objects.get(id=course_id)
        
        # Remove the course from student's courses
        student.courses.remove(course)
        
        # Also remove any grades associated with this course
        Grade.objects.filter(student=student, course=course).delete()
        
        # Recalculate GPA
        student.gpa = calculate_gpa(student)
        student.save(update_fields=['gpa'])
        
        return JsonResponse({'success': True})
    except (Student.DoesNotExist, Course.DoesNotExist) as e:
        return JsonResponse({'success': False, 'error': str(e)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})