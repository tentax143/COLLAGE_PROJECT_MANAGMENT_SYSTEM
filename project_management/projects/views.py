from django.shortcuts import render
from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse
import os
from django.conf import settings
from .models import Student,User,faculty_master,Project,assignreviewers,regulation_master,Student_cgpa,Course
import datetime
from django.contrib import messages
import hashlib
from django.db import connections


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
    
    return render(request, 'student/student_login.html')
from django.db import connections

def student_entry(request):
    student_regno = request.session.get('student_regno')
    if not student_regno:
        return render(request, 'error.html', {'message': 'Student registration number not found in session.'})

    # Retrieve student details
    with connections['rit_cgpatrack'].cursor() as cursor:
        cursor.execute("SELECT student_name FROM application_student WHERE reg_no = %s", [student_regno])
        row = cursor.fetchone()
    
    student_name = row[0] if row else "Unknown"

    # Check if a project has already been submitted
    existing_project = Project.objects.filter(reg_no=student_regno).first()

    if existing_project:
        return render(request, 'student/student_entry.html', {
            'student_regno': student_regno,
            'student_name': student_name,
            'project': existing_project,  # Pass existing project details
            'submitted': True  # Flag to indicate form should not be shown
        })

    faculty_list = faculty_master.objects.all()

    if request.method == 'POST':
        Project_title = request.POST.get('title')
        domain = request.POST.get('domain')
        project_type = request.POST.get('type')

        if project_type == 'internal':
            internal_guide_name = request.POST.get('internal_guide_name')
        elif project_type == 'external':
            company_name = request.POST.get('company_name')
            location = request.POST.get('location')
            company_guide_name = request.POST.get('company_guide_name')
            duration = request.POST.get('duration')

        # Validate required fields
        if project_type == 'internal' and not all([Project_title, domain, project_type, internal_guide_name]):
            return render(request, 'student/student_entry.html', {
                'faculty_list': faculty_list,
                'student_regno': student_regno,
                'error': 'All fields are required for internal projects.'
            })
        elif project_type == 'external' and not all([Project_title, domain, project_type, company_name, location, company_guide_name, duration]):
            return render(request, 'student/student_entry.html', {
                'faculty_list': faculty_list,
                'student_regno': student_regno,
                'error': 'All fields are required for external projects.'
            })

        # Save project details
        project = Project.objects.create(
            title=Project_title,
            domain=domain,
            project_type=project_type,
            internal_guide_name=internal_guide_name if project_type == 'internal' else None,
            company_name=company_name if project_type == 'external' else None,
            location=location if project_type == 'external' else None,
            company_guide_name=company_guide_name if project_type == 'external' else None,
            duration=duration if project_type == 'external' else None,
            reg_no=student_regno,
            student_name=student_name
        )

        return redirect('student_entry')  # Refresh page to show submitted status

    return render(request, 'student/student_entry.html', {
        'faculty_list': faculty_list,
        'student_regno': student_regno,
        'title': "Student Entry",
        'submitted': False  # Flag to indicate form should be shown
    })


def view_marks(request):
    return render(request, 'student/view_marks.html')
def view_status(request):
    return render(request, 'student/view_status.html')

#################faculty part#######################################



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

    return render(request, 'faculty/faculty_login.html')


def hod_dashbord(request):
    # Retrieve session data
    role = request.session.get('role')
    department = request.session.get('department')
    name = request.session.get('name')

    projects_list = Project.objects.filter(department=department)
    
    return render(request, 'faculty/hod_dashbord.html', {
        'projects_list': projects_list,
        'role': role,
        'department': department,
        'name': name
    })
# def allocate_commity(request):
#     return render(request, 'allocate_commity.html')
from django.shortcuts import render, redirect
from .models import Course, assignreviewers

def review1(request):
    role = request.session.get('role')
    department = request.session.get('department')
    name = request.session.get('name')

    department_mapping = {
        "ARTIFICIAL INTELLIGENCE AND DATA SCIENCE": "B.TECH AD",
        "COMPUTER SCIENCE AND ENGINEERING": "B.TECH CSE",
        "INFORMATION TECHNOLOGY": "B.TECH IT",
    }
    course_department = department_mapping.get(department, department)

    # Fetch courses only for 8th semester
    courses = Course.objects.using('course_master').filter(department=course_department, semester=8)
    
    projects_list = Project.objects.filter(department=department)
    regulation = regulation_master.objects.using('course_master').all()
    faculty_list = User.objects.using('rit_e_approval').filter(Department=department)
    print(faculty_list,"working")

    if request.method == "POST":
        review_type = "Review 1"
        reviewer1 = request.POST.get("reviewer1")
        reviewer2 = request.POST.get("reviewer2")
        reviewer3 = request.POST.get("reviewer3")
        regulation_selected = request.POST.get("regulation")



        # Get the course details (assuming one course per department for now)
        if courses.exists():
            course = courses.first()
            course_code = course.course_code
            course_name = course.course_title
            batch = course.batch
            sem = course.semester
        else:
            course_code = ""
            course_name = ""
            batch = ""
            sem = ""

        # Save the data in the assignreviewers table
        assignreviewers.objects.create(
            review_type=review_type,
            reviewer1=reviewer1,
            reviewer2=reviewer2,
            reviewer3=reviewer3,
            regulation=regulation_selected,
            coursecode=course_code,
            coursename=course_name,
            batch=batch,
            sem=sem,
            department=department

        )

        return redirect("review1")  # Redirect to avoid form resubmission

    return render(request, "faculty/review/review1.html", {
        "projects_list": projects_list,
        "role": role,
        "department": department,
        "name": name,
        "faculty_list": faculty_list,
        "regulation": regulation,
        "courses": courses,
    })



def review2(request):
    role = request.session.get('role')
    department = request.session.get('department')
    name = request.session.get('name')
    department_mapping = {
        "ARTIFICIAL INTELLIGENCE AND DATA SCIENCE": "B.TECH AD",
        "COMPUTER SCIENCE AND ENGINEERING": "B.TECH CSE",
        "INFORMATION TECHNOLOGY": "B.TECH IT",
    }
    course_department = department_mapping.get(department, department)
    courses = Course.objects.using('course_master').filter(department=course_department, semester=8)
    projects_list = Project.objects.filter(department=department)
    regulation = regulation_master.objects.using('course_master').all()
    faculty_list = User.objects.using('rit_e_approval').filter(Department=department)
    # projects_list = Project.objects.all()
    if request.method == "POST":
        review_type = "Review 2"
        reviewer1 = request.POST.get("reviewer1")
        reviewer2 = request.POST.get("reviewer2")
        reviewer3 = request.POST.get("reviewer3")
        regulation_selected = request.POST.get("regulation")



        # Get the course details (assuming one course per department for now)
        if courses.exists():
            course = courses.first()
            course_code = course.course_code
            course_name = course.course_title
            batch = course.batch
            sem = course.semester
        else:
            course_code = ""
            course_name = ""
            batch = ""
            sem = ""

        # Save the data in the assignreviewers table
        assignreviewers.objects.create(
            review_type=review_type,
            reviewer1=reviewer1,
            reviewer2=reviewer2,
            reviewer3=reviewer3,
            regulation=regulation_selected,
            coursecode=course_code,
            coursename=course_name,
            batch=batch,
            sem=sem,
            department=department

        )

    
    return render(request, 'faculty/review/review2.html', {
        "projects_list": projects_list,
        "role": role,
        "department": department,
        "name": name,
        "faculty_list": faculty_list,
        "regulation": regulation,
        "courses": courses,
    })
def review3(request):
    role = request.session.get('role')
    department = request.session.get('department')
    name = request.session.get('name')

    department_mapping = {
        "ARTIFICIAL INTELLIGENCE AND DATA SCIENCE": "B.TECH AD",
        "COMPUTER SCIENCE AND ENGINEERING": "B.TECH CSE",
        "INFORMATION TECHNOLOGY": "B.TECH IT",
    }
    course_department = department_mapping.get(department, department)
    courses = Course.objects.using('course_master').filter(department=course_department, semester=8)
    projects_list = Project.objects.filter(department=department)
    regulation = regulation_master.objects.using('course_master').all()
    faculty_list = User.objects.using('rit_e_approval').filter(Department=department)

    if request.method == "POST":
        review_type = "Review 3"
        reviewer1_id = request.POST.get("reviewer1")
        reviewer2_id = request.POST.get("reviewer2")
        reviewer3_id = request.POST.get("reviewer3")
        regulation_selected = request.POST.get("regulation")
        industrial_expert_name = request.POST.get("industrial_expert_name")
        company_name = request.POST.get("company_name")
        designation = request.POST.get("designation")

        # Fetch faculty names based on selected IDs
        reviewer1 = User.objects.using('rit_e_approval').filter(id=reviewer1_id).first()
        reviewer2 = User.objects.using('rit_e_approval').filter(id=reviewer2_id).first()
        reviewer3 = User.objects.using('rit_e_approval').filter(id=reviewer3_id).first()

        reviewer1_name = reviewer1.Name if reviewer1 else ""
        reviewer2_name = reviewer2.Name if reviewer2 else ""
        reviewer3_name = reviewer3.Name if reviewer3 else ""

        # Get the course details (assuming one course per department for now)
        if courses.exists():
            course = courses.first()
            course_code = course.course_code
            course_name = course.course_title
            batch = course.batch
            sem = course.semester
        else:
            course_code = ""
            course_name = ""
            batch = ""
            sem = ""

        # Save the data in the assignreviewers table
        assignreviewers.objects.create(
            review_type=review_type,
            reviewer1=reviewer1_name,
            reviewer2=reviewer2_name,
            reviewer3=reviewer3_name,
            regulation=regulation_selected,
            coursecode=course_code,
            coursename=course_name,
            batch=batch,
            sem=sem,
            department=department,
            expname=industrial_expert_name,
            company_name=company_name,
            desegnation=designation
        )

        messages.success(request, "Reviewers Assigned Successfully!")

    return render(request, 'faculty/review/review3.html', {
        "projects_list": projects_list,
        "role": role,
        "department": department,
        "name": name,
        "faculty_list": faculty_list,
        "regulation": regulation,
        "courses": courses,
    })

from django.shortcuts import render, redirect
from .models import Project, assignreviewers, User

from django.db.models import Q

def guide_alocation(request):
    role = request.session.get('role')
    department1 = request.session.get('department')
    name = request.session.get('name')

    faculty_list = User.objects.using('rit_e_approval').filter(Department=department1)

    # Exclude projects that already have an assigned internal guide
    projects = Project.objects.filter(department=department1, internal_guide_name__isnull=True)

    if request.method == "POST":
        print("Received POST Data:", request.POST)

        student_ids = request.POST.getlist("student_ids")
        faculty_id = request.POST.get("faculty_id")

        if student_ids and faculty_id:
            faculty_id = int(faculty_id)
            faculty = User.objects.using('rit_e_approval').filter(id=faculty_id).first()

            if faculty:
                print("Faculty Found:", faculty.Name)
                faculty_name = faculty.Name  # Get faculty name

                # Search for faculty in reviewer1, reviewer2, or reviewer3
                course_details = assignreviewers.objects.filter(
                    Q(reviewer1=faculty_name) | Q(reviewer2=faculty_name) | Q(reviewer3=faculty_name),
                    department=department1
                ).first()

                if course_details:
                    print(f"Course Found: {course_details.coursecode}, {course_details.coursename}, Sem {course_details.sem}")
                    course_code = course_details.coursecode
                    course_title = course_details.coursename
                    semester = course_details.sem

                    updated_count = Project.objects.filter(id__in=student_ids).update(
                        internal_guide_name=faculty_name,
                        course_code=course_code,
                        course_title=course_title,
                        semester=semester
                    )
                    print(f"Updated {updated_count} project records.")
                else:
                    print("Error: Faculty is not listed as a reviewer in any course.")
            else:
                print("Error: Faculty not found!")

        return redirect("guide_alocation")

    return render(request, 'faculty/guide_alocation.html', {
        'projects': projects,
        'role': role,
        'department': department1,
        'name': name,
        'faculty_list': faculty_list,
    })





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

    return render(request, 'faculty/faculty_dashboard.html', context)

def review_mark_allotment(request):
    return(request,"faculty/review_mark_allotment.html")

from django.shortcuts import render

def review1_markentry(request):
    role = request.session.get('role')
    department = request.session.get('department')
    name = request.session.get('name')


    # Filter projects where department matches session department
    projects_list = Project.objects.filter(department=department)
    batches = Project.objects.values_list('batch', flat=True).distinct()
    print(projects_list,"working")

    return render(request, "faculty/review/review1_markentry.html", {
        "projects": projects_list,
        'role': role,
        'department': department,
        'name': name,
        'batches': batches
    })


def review2_markentry(request):
    return render(request, "faculty/review/review2_markentry.html")
def review3_markentry(request):
    return render(request, "faculty/review/review3_markentry.html")

def admin_portal(request):
    return(request,"e-approval/page.html")


