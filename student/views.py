from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from .models import Student, calculate_gpa,Grade
from .forms import GradeForm
from users.utils import is_faculty_or_admin
from task.models import Task

def get_student_context(user):
    student = Student.objects.get(user=user)
    grades = Grade.objects.filter(student=student)
    courses = student.courses.all()
    gpa = calculate_gpa(student)

    context = {
        'student': student,
        'grades': grades,
        'courses': courses,
        'gpa': gpa
    }

    return context

@login_required
@user_passes_test(is_faculty_or_admin)
def manage_student(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    grades = student.grades.all()
    courses = student.courses.all()
    gpa = calculate_gpa(student)# This will ensure we have the most up-to-date GPA

    # Handle grade assignment
    form = GradeForm(request.POST or None, student=student)
    if request.method == 'POST' and 'submit_grade' in request.POST:
        if form.is_valid():
            grade = form.save()
            # Recalculate GPA
            student.gpa = calculate_gpa(student)
            student.save(update_fields=['gpa'])
            messages.success(request, f"Grade for {student.user.username} saved.")
            return redirect('manage_student', student_id=student_id)

    return render(request, 'users/manage_student.html', {
        'student': student,
        'grades':  grades,
        'courses': courses,
        'gpa':     gpa,
        'grade_form': form,
    })