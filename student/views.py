from django.shortcuts import render
from django.http import HttpResponse
def student_list(request):
    return HttpResponse("Student list view here.")

def student_detail(request, pk):
    return HttpResponse(f"Student detail view for student ID {pk}")
