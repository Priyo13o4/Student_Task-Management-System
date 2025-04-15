from django.shortcuts import render
from django.http import HttpResponse
def task_list(request):
    return HttpResponse("Task list view here.")

def task_detail(request, pk):
    return HttpResponse(f"Task detail view for task ID {pk}")