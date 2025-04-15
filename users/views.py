from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

def home_redirect(request):
    return redirect('login')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect based on role
            if user.role == "admin":
                return redirect("admin_dashboard")
            elif user.role == "faculty":
                return redirect("faculty_dashboard")
            elif user.role == "student":
                return redirect("student_dashboard")
        else:
            messages.error(request, "Invalid credentials.")
    
    return render(request, "users/login.html")

@login_required
def logout_view(request):
    logout(request)
    return redirect("login")
@login_required
def admin_dashboard(request):
    return render(request, "users/admin_dashboard.html")

@login_required
def faculty_dashboard(request):
    return render(request, "users/faculty_dashboard.html")

@login_required
def student_dashboard(request):
    return render(request, "users/student_dashboard.html")