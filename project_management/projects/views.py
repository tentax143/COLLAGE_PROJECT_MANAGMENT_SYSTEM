from django.shortcuts import render
from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse
import os
from django.conf import settings
from .models import Student,User
import datetime
from django.contrib import messages
import hashlib


def encrypt_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def home_page(request):
    return render(request, 'home.html')
def student_login(request):
    if request.method == 'POST':
        student_regno = request.POST.get('regno')
        student_password = request.POST.get('password')
        student_password_eny = encrypt_password(student_password)
        print(student_regno,student_password)
        try:
            student = Student.objects.using('placement_portal').get(student_regno=student_regno)
            if student.student_password == student_password_eny:
                # Store `student_regno` and `student_name` in the session
                request.session['student_regno'] = student_regno
                # Redirect to `process_tk`
                return redirect('student_entry')
            else:
                messages.error(request, 'Invalid password')
        
        except Student.DoesNotExist:
            messages.error(request, 'Student not found')
    
    return render(request, 'student_login.html')
def faculty_login(request):
    if request.method == "POST":
        username = request.POST.get('username')  # This will map to `staff_id`
        password = request.POST.get('password')

        print(f"Attempting to log in with staff_id: {username} and password: {password}")

        # Custom authentication check
        try:
            user = User.objects.using('rit_e_approval').get(staff_id=username)
            
            # Manually check the password
            if encrypt_password(password)==user.Password: 
                print(encrypt_password(password),user.Password) # Assuming passwords are hashed
                print("Authentication successful!")
                
                # Create a session or any custom login logic
                request.session['user_id'] = user.id  # Store user ID in session
                request.session['role'] = user.role  # Store the role if needed
                
                return redirect('faculty_dashboard')  # Redirect to the appropriate page
            else:
                print("Authentication failed! Incorrect password.")
        except User.DoesNotExist:
            print("Authentication failed! User not found.")

        return render(request, 'faculty_login.html', {'error': 'Invalid credentials!'})

    return render(request, 'faculty_login.html')

def student_entry(request):
    return render(request, 'student_entry.html')
def faculty_dashboard(request):
    return render(request, 'faculty_dashboard.html')

