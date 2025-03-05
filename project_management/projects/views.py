from django.shortcuts import render
from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse
import os
from django.conf import settings
from .models import Student,User,faculty_master,Project
import datetime
from django.contrib import messages
import hashlib


def encrypt_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def home_page(request):
    return render(request, 'home.html')

#####################student part##################################

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
def student_entry(request):
    # Retrieve student_regno from the session
    student_regno = request.session.get('student_regno')  # This will return None if the key doesn't exist
    
    if not student_regno:
        # Handle the case where student_regno is not found in the session
        return render(request, 'error.html', {'message': 'Student registration number not found in session.'})

    # Department and batch calculation
    filter_department = int(student_regno[6:9])
    
    department_mapping = {
        243: "AI&DS",
        312: "CSBS",
        102: "EEE",
        103: "MECH",
        104: "IT",
        101: "Civil",
    }
    department = department_mapping.get(filter_department, "Unknown Department")
    
    batch1 = student_regno[4:6]
    m = int(batch1)
    batch = f"20{batch1}-20{m+4}"
    lat = int(student_regno[-3])
    entry_status = "Lateral" if lat == 3 else "Transfer" if lat == 7 else "Regular"
    print("working", entry_status, batch, department)

    title = "Student Entry"  # Defining title here
    
    # Fetch faculty list before POST handling
    faculty_list = faculty_master.objects.all()

    if request.method == 'POST':
        Project_title = request.POST.get('title')  # Matches 'name="title"'
        domain = request.POST.get('domain')  # Matches 'name="domain"'
        project_type = request.POST.get('type')  # Matches 'name="type"'

        if project_type == 'internal':
            internal_guide_name = request.POST.get('internal_guide_name')
        elif project_type == 'external':
            company_name = request.POST.get('company_name')
            location = request.POST.get('location')
            company_guide_name = request.POST.get('company_guide_name')
            duration = request.POST.get('duration')

        

        # Validate the required fields
        if project_type == 'internal':
            if not all([Project_title, domain, project_type, internal_guide_name]):
                return render(request, 'student_entry.html', {
                    'faculty_list': faculty_list,
                    'student_regno': student_regno,
                    'title': title,
                    'error': 'All fields are required for internal projects.'
                })
        elif project_type == 'external':
            if not all([Project_title, domain, project_type, company_name, location, company_guide_name, duration]):
                return render(request, 'student_entry.html', {
                    'faculty_list': faculty_list,
                    'student_regno': student_regno,
                    'title': title,
                    'error': 'All fields are required for external projects.'
                })

        # Create the Project entry
        if project_type == 'external':
            Project.objects.create(
                department=department,
                batch=batch,
                entry_status=entry_status,
                title=Project_title,
                domain=domain,
                project_type=project_type,
                company_name=company_name,
                location=location,
                company_guide_name=company_guide_name,
                duration=duration,
            )
        elif project_type == 'internal':
            Project.objects.create(
                department=department,
                batch=batch,
                entry_status=entry_status,
                title=Project_title,
                domain=domain,
                project_type=project_type,
                internal_guide_name=internal_guide_name,
            )

    return render(request, 'student_entry.html', {'faculty_list': faculty_list, 'student_regno': student_regno, 'title': title})

def view_marks(request):
    return render(request, 'view_marks.html')
def view_status(request):
    return render(request, 'view_status.html')

#################faculty part#######################################

def hod_dashbord(request):
    return render(request, 'hod_dashbord.html')


def faculty_login(request):
    if request.method == "POST":
        username = request.POST.get('username')  # This will map to `staff_id`
        password = request.POST.get('password')

        print(f"Attempting to log in with staff_id: {username} and password: {password}")

        try:
            user = User.objects.using('rit_e_approval').get(staff_id=username)
            if encrypt_password(password) == user.Password:
                print("Authentication successful!")

                # Store necessary details in session
                request.session['user_id'] = user.id
                request.session['role'] = user.role
                request.session['department'] = user.Department  # Correct (matches your model)  # Store faculty department
                request.session['name'] = user.Name
                if user.role =='HOD':
                    return redirect('hod_dashbord')


                return redirect('faculty_dashboard')  # Redirect after successful login
            else:
                print("Authentication failed! Incorrect password.")
        except User.DoesNotExist:
            print("Authentication failed! User not found.")

        return render(request, 'faculty_login.html', {'error': 'Invalid credentials!'})

    return render(request, 'faculty_login.html')


def faculty_dashboard(request):
    # Ensure user is logged in and department is stored
    if 'department' not in request.session:
        return redirect('faculty_login')  # Redirect if session is not set

    faculty_department = request.session['department']

    # Fetch only projects that belong to the faculty's department
    projects = Project.objects.filter(department=faculty_department)

    # Pass session data to the template
    context = {
        'projects': projects,
        'user_id': request.session.get('user_id'),
        'role': request.session.get('role'),
        'department': request.session.get('department'),
        'name': request.session.get('name'),
    }
    print(context)

    return render(request, 'faculty_dashboard.html', context)



