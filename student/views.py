from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CourseAssignmentForm
from django.contrib import messages
from django.db.models import Q
from .models import Student, calculate_gpa, Grade, Course
from .forms import GradeForm, StudentForm
from users.utils import is_faculty_or_admin, is_admin
from task.models import Task
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from courses.forms import CourseForm
import csv
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from django.utils.text import slugify




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
        
        # Update attendance
        try:
            attendance = float(request.POST.get('attendance', 0))
            if 0 <= attendance <= 100:
                student.attendance = attendance
            else:
                messages.error(request, "Attendance must be between 0 and 100.")
                return redirect('manage_student', student_id=student_id)
        except ValueError:
            messages.error(request, "Invalid attendance value.")
            return redirect('manage_student', student_id=student_id)
        
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
    
#Export stuff 

@login_required
def export_grades_csv(request, student_id=None):
    if student_id:
        # For student view
        student = get_object_or_404(Student, pk=student_id)
        if not (request.user.is_staff or request.user == student.user):
            return HttpResponse('Unauthorized', status=401)
        grades = Grade.objects.filter(student=student)
    else:
        # For admin view
        if not request.user.is_staff:
            return HttpResponse('Unauthorized', status=401)
        grades = Grade.objects.all()

    response = HttpResponse(content_type='text/csv')
    filename = f'grades_{student.register_no if student_id else "all"}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    
    if student_id:
        # For individual student view
        writer.writerow(['Student Name:', f'{student.user.first_name} {student.user.last_name}'])
        writer.writerow(['Register No:', student.register_no])
        writer.writerow([])  # Empty row for spacing
        writer.writerow(['Course Code', 'Course Name', 'Grade'])
        writer.writerow([])  # Empty row for spacing
        
        for grade in grades:
            writer.writerow([
                grade.course.code,
                grade.course.name,
                grade.grade
            ])
        
        writer.writerow([])  # Empty row for spacing
        writer.writerow(['Total GPA:', student.gpa])
    else:
        # For admin view (all students)
        current_student = None
        for grade in grades:
            student = grade.student
            if current_student != student:
                if current_student is not None:
                    writer.writerow(['Total GPA:', current_student.gpa])
                    writer.writerow([])  # Empty row for spacing between students
                writer.writerow(['Register No:', student.register_no])
                writer.writerow(['Course Code', 'Course Name', 'Grade'])
                writer.writerow([])  # Empty row for spacing
                current_student = student
            
            writer.writerow([
                grade.course.code,
                grade.course.name,
                grade.grade
            ])
        
        if current_student is not None:
            writer.writerow([])  # Empty row for spacing
            writer.writerow(['Total GPA:', current_student.gpa])

    return response

@login_required
def export_grades_pdf(request, student_id=None):
    if student_id:
        # For student view
        student = get_object_or_404(Student, pk=student_id)
        if not (request.user.is_staff or request.user == student.user):
            return HttpResponse('Unauthorized', status=401)
        grades = Grade.objects.filter(student=student)
    else:
        # For admin view
        if not request.user.is_staff:
            return HttpResponse('Unauthorized', status=401)
        grades = Grade.objects.all()

    response = HttpResponse(content_type='application/pdf')
    filename = f'grades_{student.register_no if student_id else "all"}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    p.setFont("Helvetica-Bold", 16)
    title = f"Grades Report - {student.register_no if student_id else 'All Students'}"
    p.drawString(50, height - 50, title)

    y_position = height - 100  # Starting position for content

    if student_id:
        # For individual student view
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y_position, f"Student Name: {student.user.first_name} {student.user.last_name}")
        y_position -= 20
        p.drawString(50, y_position, f"Register No: {student.register_no}")
        y_position -= 30

        # Table data
        data = [['Course Code', 'Course Name', 'Grade']]
        for grade in grades:
            data.append([
                grade.course.code,
                grade.course.name,
                grade.grade
            ])

        # Add GPA at the bottom
        data.append(['', '', ''])
        data.append(['Total GPA:', '', str(student.gpa)])

    else:
        # For admin view (all students)
        current_student = None
        data = []
        
        for grade in grades:
            student = grade.student
            if current_student != student:
                if current_student is not None:
                    data.append(['', '', ''])
                    data.append(['Total GPA:', '', str(current_student.gpa)])
                    data.append(['', '', ''])
                    data.append(['', '', ''])
                
                data.append(['Register No:', student.register_no, ''])
                data.append(['Course Code', 'Course Name', 'Grade'])
                current_student = student
            
            data.append([
                grade.course.code,
                grade.course.name,
                grade.grade
            ])
        
        if current_student is not None:
            data.append(['', '', ''])
            data.append(['Total GPA:', '', str(current_student.gpa)])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    # Draw table
    table.wrapOn(p, width - 100, height - 100)
    table.drawOn(p, 50, y_position - 300)

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response