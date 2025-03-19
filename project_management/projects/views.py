from django.shortcuts import render
from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse
import os
from django.conf import settings
from .models import Student,User,faculty_master,Project,assignreviewers,regulation_master,Student_cgpa,Course,review_marks_master
import datetime
from django.contrib import messages
import hashlib
from django.db import connections


def encrypt_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def home_page(request):
    return render(request, 'home.html')

#↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓student part↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓

def student_login(request):
    if request.method == 'POST':
        student_regno = request.POST.get('regno')
        student_password = request.POST.get('password')
        student_password_eny = encrypt_password(student_password)
        print(student_regno,student_password)
        try:
            student = Student.objects.using('placement_portal').get(student_regno=student_regno)
            if student.student_password == student_password_eny:
                # Store student registration number
                request.session['student_regno'] = student_regno
                
                # Retrieve the student's name from rit_cgpatrack database
                with connections['rit_cgpatrack'].cursor() as cursor:
                    cursor.execute("SELECT student_name FROM application_student WHERE reg_no = %s", [student_regno])
                    row = cursor.fetchone()
                student_name = row[0] if row else "Unknown"
                
                # Calculate department from registration number
                try:
                    filter_department = int(student_regno[6:9])
                except ValueError:
                    filter_department = None
                    
                department_mapping = {
                    243: "ARTIFICIAL INTELLIGENCE AND DATA SCIENCE",
                    107: "COMPUTER SCIENCE AND BUSINESS SYSTEM",
                    106: "ELECTRONICS AND COMMUNICATION ENGINEERING",
                    102: "MECHANICAL ENGINEERING",
                    105: "INFORMATION TECHNOLOGY",
                    101: "CIVIL ENGINEERING",
                    104: "COMPUTER SCIENCE AND ENGINEERING",
                    103: "ELECRICAL AND ELECTRONICS ENGINEERING",
                }
                department = department_mapping.get(filter_department, "Unknown Department")
                
                # Store all student details in session
                request.session['student_name'] = student_name
                request.session['department'] = department
                
                return redirect('student_entry')
            else:
                messages.error(request, 'Invalid password')
        
        except Student.DoesNotExist:
            messages.error(request, 'Student not found')
    
    return render(request, 'student/student_login.html')

def student_entry(request):
    # Retrieve student_regno from the session
    student_regno = request.session.get('student_regno')
    student_name = request.session.get('student_name')
    department = request.session.get('department')
    
    if not student_regno or not student_name or not department:
        return render(request, 'error.html', {'message': 'Student information not found in session.'})

    # Check if a project already exists for this student.
    existing_project = Project.objects.filter(reg_no=student_regno).first()
    if existing_project:
        return render(request, 'student/student_entry.html', {
            'student_regno': student_regno,
            'student_name': student_name,
            'project': existing_project,  # Pass existing project details
            'submitted': True  # Flag to indicate form should not be shown
        })

    title = "Student Entry"
    faculty_list = faculty_master.objects.all()
    
    if request.method == 'POST':
        Project_title = request.POST.get('title')
        domain = request.POST.get('domain')
        project_type = request.POST.get('type')
    
        if project_type == 'internal':
            internal_guide_name = request.POST.get('internal_guide_name')
            # Validate required fields for internal projects
            if not all([Project_title, domain, project_type, internal_guide_name]):
                messages.error(request, 'All fields are required for internal projects.')
                return render(request, 'student/student_entry.html', {
                    'faculty_list': faculty_list,
                    'student_regno': student_regno,
                    'title': title
                })
        elif project_type == 'external':
            company_name = request.POST.get('company_name')
            location = request.POST.get('location')
            company_guide_name = request.POST.get('company_guide_name')
            duration = request.POST.get('duration')
            # Validate required fields for external projects
            if not all([Project_title, domain, project_type, company_name, location, company_guide_name, duration]):
                messages.error(request, 'All fields are required for external projects.')
                return render(request, 'student/student_entry.html', {
                    'faculty_list': faculty_list,
                    'student_regno': student_regno,
                    'title': title
                })
    
        # Calculate batch from student_regno
        batch1 = student_regno[4:6]
        try:
            m = int(batch1)
            batch = f"20{batch1}-20{m+4}"
        except ValueError:
            batch = "Unknown Batch"
        
        # Calculate entry_status from student_regno
        try:
            lat = int(student_regno[-3])
        except ValueError:
            lat = 0
        entry_status = "Lateral" if lat == 3 else "Transfer" if lat == 7 else "Regular"

        # Create the project entry based on the project type
        if project_type == 'external':
            project = Project.objects.create(
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
                reg_no=student_regno,
                student_name=student_name
            )
        elif project_type == 'internal':
            project = Project.objects.create(
                department=department,
                batch=batch,
                entry_status=entry_status,
                title=Project_title,
                domain=domain,
                project_type=project_type,
                internal_guide_name=internal_guide_name,
                reg_no=student_regno,
                student_name=student_name
            )
    
        # After creating the project, redirect to success page
        return render(request, 'student/success.html', {
            'student_regno': student_regno,
            'student_name': student_name,
        })
    
    # For GET requests, simply render the form
    return render(request, 'student/student_entry.html', {
        'faculty_list': faculty_list,
        'student_regno': student_regno,
        'title': title
    })



def view_marks(request):
    student_regno = request.session.get('student_regno')
    student_name = request.session.get('student_name')
    department = request.session.get('department')

    student_marks = review_marks_master.objects.filter(
        student_name=student_name,
        reg_no=student_regno
    ).order_by('review_number')

    review_marks = {1: {'individual': [], 'cumulative': {}}, 
                   2: {'individual': [], 'cumulative': {}}, 
                   3: {'individual': [], 'cumulative': {}}}
    
    for mark in student_marks:
        review_num = mark.review_number
        mark_dict = {
            'reviewer_type': mark.reviewer_type,
            'faculty_name': mark.faculty_name,
            'criteria_1': mark.criteria_1,
            'criteria_2': mark.criteria_2,
            'criteria_3': mark.criteria_3,
            'criteria_4': mark.criteria_4,
            'criteria_5': mark.criteria_5,
            'criteria_6': mark.criteria_6,
            'criteria_7': mark.criteria_7,
            'criteria_8': mark.criteria_8,
            'criteria_9': mark.criteria_9,
            'criteria_10': mark.criteria_10,
            'total': mark.total
        }
        review_marks[review_num]['individual'].append(mark_dict)

        # Calculate cumulative marks for each review
        if review_marks[review_num]['individual']:
            marks_list = review_marks[review_num]['individual']
            cumulative = {
                'criteria_1': sum(m['criteria_1'] for m in marks_list) / len(marks_list),
                'criteria_2': sum(m['criteria_2'] for m in marks_list) / len(marks_list),
                'criteria_3': sum(m['criteria_3'] for m in marks_list) / len(marks_list),
                'criteria_4': sum(m['criteria_4'] for m in marks_list) / len(marks_list),
                'criteria_5': sum(m['criteria_5'] for m in marks_list) / len(marks_list),
                'criteria_6': sum(m['criteria_6'] for m in marks_list) / len(marks_list),
                'criteria_7': sum(m['criteria_7'] for m in marks_list) / len(marks_list),
                'criteria_8': sum(m['criteria_8'] for m in marks_list) / len(marks_list),
                'criteria_9': sum(m['criteria_9'] for m in marks_list) / len(marks_list),
                'criteria_10': sum(m['criteria_10'] for m in marks_list) / len(marks_list),
            }
            cumulative['total'] = sum(cumulative.values())
            review_marks[review_num]['cumulative'] = cumulative

    return render(request, 'student/view_marks.html', {
        'student_regno': student_regno,
        'student_name': student_name,
        'department': department,
        'review_marks': review_marks,
    })


def view_status(request):
    return render(request, 'student/view_status.html')


#↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑#student part↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
#↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓#faculty part↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓



def faculty_login(request):
    if request.method == "POST":
        username = request.POST.get('username')  # This maps to staff_id
        password = request.POST.get('password')

        print(f"Attempting to log in with staff_id: {username} and password: {password}")

        # Use filter() to retrieve all matching users instead of get()
        users = User.objects.using('rit_e_approval').filter(staff_id=username)
        
        if not users.exists():
            # No user found with this staff_id
            print(f"No user found with staff_id: {username}")
            return render(request, 'faculty/faculty_login.html', {'error': 'User not found!'})
        elif users.count() >= 2:
            user = users[1]  # Select the second user if more than one exists
        else:
            user = users.first()
        
        print(user, "the selected user is")
        
        # Check the password (replace encrypt_password with your actual hash comparison)
        if encrypt_password(password) == user.Password:
            print("Authentication successful!")
            # Store necessary details in session
            request.session['user_id'] = user.id
            request.session['role'] = user.role
            request.session['department'] = user.Department  # Faculty department
            request.session['name'] = user.Name
            
            if user.role == 'HOD':
                return redirect('hod_dashbord')
            elif user.role == 'Staff':
                return redirect('faculty_dashboard')
        else:
            print("Authentication failed! Incorrect password.")
            return render(request, 'faculty/faculty_login.html', {'error': 'Invalid credentials!'})
    
    return render(request, 'faculty/faculty_login.html')





#↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ hod part ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓


from django.db.models import Q
from datetime import datetime
def hod_dashbord(request):
    # Retrieve session data
    role = request.session.get('role')
    department = request.session.get('department')
    name = request.session.get('name')
    projects_list = Project.objects.filter(department=department)
    a=projects_list.count()
    print(a, "the projects list is")
    print(projects_list, "the projects list is")
    batch=int(datetime.now().year)
    current_batch=f"{batch-4}-{str(batch)[2:]}"
    print(current_batch, "the current batch is")
    project_batch=f"{batch-4}-{str(batch)}"
        # Get all projects for the department from the default database
    projects_list = Project.objects.filter(department=department,batch=project_batch)
    total_projects_submitted = projects_list.count()

    # Get unique student registration numbers from projects
    submitted_student_regnos = list(projects_list.values_list('reg_no', flat=True))

    # Get all students who have marks awarded from the default database
    total_marks_awarded = review_marks_master.objects.filter(
        department=department
    ).values('reg_no').distinct().count()

    # Get all students from placement portal database
    all_students = Student_cgpa.objects.using('rit_cgpatrack').filter(batch=current_batch)
    total_students = all_students.count()

    # Get students who haven't submitted projects
    students_without_projects = Student_cgpa.objects.using('rit_cgpatrack').exclude(reg_no__in=submitted_student_regnos).filter(batch=current_batch)
    pending_submissions = students_without_projects.count()

    # Find all assignments where the internal_guide_name appears in reviewer1, reviewer2, or reviewer3
    assigned_projects = assignreviewers.objects.filter(
        department=department
    ).filter(
        Q(reviewer1=name) | Q(reviewer2=name) | Q(reviewer3=name)
    )

    # Get project list where the internal_guide_name matches the logged-in user and is assigned as a reviewer
    filtered_students_list = Project.objects.filter(
        department=department,
        internal_guide_name=name,
        batch__in=assigned_projects.values_list('batch', flat=True)
    )

    # Get student names from placement portal for students without projects
    students_without_projects_list = []
   
    without_projects = Student_cgpa.objects.using('rit_cgpatrack').exclude(reg_no__in=submitted_student_regnos).filter(batch=current_batch)
    students_without_projects_list.extend(without_projects)
    # for student in students_without_projects:
    #     # Get student name from rit_cgpatrack database
       
            
    #     students_without_projects_list.append({
    #         'regno': student.student_regno,
    #         'name': student.student_name
    #     })
    return render(request, 'faculty/hod_dashbord.html', {
        'projects_list': projects_list,
        'filtered_students_list': filtered_students_list,
        'role': role,
        'department': department,
        'name': name,
        'total_students': total_students,
        'total_projects_submitted': total_projects_submitted,
        'total_marks_awarded': total_marks_awarded,
        'pending_submissions': pending_submissions,
        'students_without_projects': students_without_projects_list
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
        "MECHANICAL ENGINEERING":"BE.MECH"
    }
    course_department = department_mapping.get(department, department)

    # Fetch courses only for 8th semester
    courses = Course.objects.using('course_master').filter(department=course_department, semester=8)
    
    projects_list = Project.objects.filter(department=department)
    regulation = regulation_master.objects.using('course_master').all()
    faculty_list = User.objects.using('rit_e_approval').filter(Department=department)

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

            # Update all projects in this department with course details
            Project.objects.filter(department=department).update(
                course_code=course_code,
                course_title=course_name,
                semester=sem
            )
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

        return redirect("review1")

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

            # Update all projects in this department with course details
            Project.objects.filter(department=department).update(
                course_code=course_code,
                course_title=course_name,
                semester=sem
            )
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

        return redirect("review2")

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

            # Update all projects in this department with course details
            Project.objects.filter(department=department).update(
                course_code=course_code,
                course_title=course_name,
                semester=sem
            )
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
    
    # Get projects that do NOT have an internal guide assigned yet
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
                
                # Directly assign faculty as the internal guide
                updated_count = Project.objects.filter(id__in=student_ids).update(
                    internal_guide_name=faculty.Name
                )
                print(f"Updated {updated_count} project records.")
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








def review_mark_allotment(request):
    return(request,"faculty/review_mark_allotment.html")

from django.shortcuts import render

from django.shortcuts import render, redirect
from .models import review_marks_master, Project

from django.shortcuts import render, redirect
from .models import review_marks_master, Project, assignreviewers

def review1_markentry(request):
    role = request.session.get('role')
    department = request.session.get('department')
    name = request.session.get('name')

    if request.method == "POST":
        faculty_name = name
        faculty_role = role
        student_name = request.POST.get('student_name')
        reg_no = request.POST.get('reg_no')
        semester_value = request.POST.get('semester')
        try:
            semester = int(semester_value) if semester_value not in [None, ''] else 0
        except ValueError:
            semester = 0
        
        course_code = request.POST.get('course_code')
        course_title = request.POST.get('course_title')
        reviewer_type = request.POST.get('reviewer_type')
        
        # Get marks for each criteria
        criteria_1 = int(request.POST.get('criteria_1', 0))
        criteria_2 = int(request.POST.get('criteria_2', 0))
        criteria_3 = int(request.POST.get('criteria_3', 0))
        criteria_4 = int(request.POST.get('criteria_4', 0))
        criteria_5 = int(request.POST.get('criteria_5', 0))
        criteria_6 = int(request.POST.get('criteria_6', 0))
        criteria_7 = int(request.POST.get('criteria_7', 0))
        criteria_8 = int(request.POST.get('criteria_8', 0))
        criteria_9 = int(request.POST.get('criteria_9', 0))
        criteria_10 = int(request.POST.get('criteria_10', 0))
        
        total = (criteria_1 + criteria_2 + criteria_3 + criteria_4 + criteria_5 +
                criteria_6 + criteria_7 + criteria_8 + criteria_9 + criteria_10)
        
        assign_record = assignreviewers.objects.filter(coursecode=course_code, department=department).first()
        if assign_record:
            batch = assign_record.batch
            regulations = assign_record.regulation  
            company_guide_name = assign_record.company_name
        else:
            batch = ""
            regulations = ""
            company_guide_name = ""

        # Create the review_marks_master record
        review_marks_master.objects.create(
            faculty_name=faculty_name,
            faculty_role=faculty_role,
            reviewer_type=reviewer_type,
            student_name=student_name,
            reg_no=reg_no,
            batch=batch,
            review_number=1,
            regulations=regulations,
            department=department,
            semester=semester,
            course_code=course_code,
            company_guide_name=company_guide_name,
            internal_guide_name=faculty_name,
            criteria_1=criteria_1,
            criteria_2=criteria_2,
            criteria_3=criteria_3,
            criteria_4=criteria_4,
            criteria_5=criteria_5,
            criteria_6=criteria_6,
            criteria_7=criteria_7,
            criteria_8=criteria_8,
            criteria_9=criteria_9,
            criteria_10=criteria_10,
            total=total,
        )
        return redirect('review1_markentry')

    # For GET requests, handle the display logic
    projects_list = Project.objects.filter(department=department)
    
    # Check if faculty is assigned as a reviewer
    assigned_as_reviewer = assignreviewers.objects.filter(
        department=department
    ).filter(
        Q(reviewer1=name) | Q(reviewer2=name) | Q(reviewer3=name)
    ).exists()

    # Check if faculty is assigned as a guide
    assigned_as_guide = Project.objects.filter(
        department=department,
        internal_guide_name=name
    ).exists()

    # Get list of students where marks haven't been entered yet
    marked_as_guide = review_marks_master.objects.filter(
        faculty_name=name,
        reviewer_type='Guide',
        review_number=1
    ).values_list('reg_no', flat=True)

    marked_as_reviewer = review_marks_master.objects.filter(
        faculty_name=name,
        reviewer_type='Reviewer',
        review_number=1
    ).values_list('reg_no', flat=True)

    # Get students for guide role
    guide_students = Project.objects.filter(
        department=department,
        internal_guide_name=name
    ).exclude(reg_no__in=marked_as_guide)

    # Get students for reviewer role
    if assigned_as_reviewer:
        reviewer_students = Project.objects.filter(
            department=department,
            batch__in=assignreviewers.objects.filter(
                Q(reviewer1=name) | Q(reviewer2=name) | Q(reviewer3=name)
            ).values_list('batch', flat=True)
        ).exclude(reg_no__in=marked_as_reviewer)
    else:
        reviewer_students = Project.objects.none()

    return render(request, "faculty/review/review1_markentry.html", {
        "projects": projects_list,
        'role': role,
        'department': department,
        'name': name,
        'guide_students': guide_students,
        'reviewer_students': reviewer_students,
        'is_guide': assigned_as_guide,
        'is_reviewer': assigned_as_reviewer
    })





def review2_markentry(request):
    role = request.session.get('role')
    department = request.session.get('department')
    name = request.session.get('name')

    if request.method == "POST":
        faculty_name = name
        faculty_role = role
        student_name = request.POST.get('student_name')
        reg_no = request.POST.get('reg_no')
        semester_value = request.POST.get('semester')
        try:
            semester = int(semester_value) if semester_value not in [None, ''] else 0
        except ValueError:
            semester = 0
        
        course_code = request.POST.get('course_code')
        course_title = request.POST.get('course_title')
        reviewer_type = request.POST.get('reviewer_type')
        
        # Get marks for each criteria
        criteria_1 = int(request.POST.get('criteria_1', 0))
        criteria_2 = int(request.POST.get('criteria_2', 0))
        criteria_3 = int(request.POST.get('criteria_3', 0))
        criteria_4 = int(request.POST.get('criteria_4', 0))
        criteria_5 = int(request.POST.get('criteria_5', 0))
        criteria_6 = int(request.POST.get('criteria_6', 0))
        criteria_7 = int(request.POST.get('criteria_7', 0))
        criteria_8 = int(request.POST.get('criteria_8', 0))
        criteria_9 = int(request.POST.get('criteria_9', 0))
        criteria_10 = int(request.POST.get('criteria_10', 0))
        
        total = (criteria_1 + criteria_2 + criteria_3 + criteria_4 + criteria_5 +
                criteria_6 + criteria_7 + criteria_8 + criteria_9 + criteria_10)
        
        assign_record = assignreviewers.objects.filter(coursecode=course_code, department=department).first()
        if assign_record:
            batch = assign_record.batch
            regulations = assign_record.regulation  
            company_guide_name = assign_record.company_name
        else:
            batch = ""
            regulations = ""
            company_guide_name = ""

        # Create the review_marks_master record
        review_marks_master.objects.create(
            faculty_name=faculty_name,
            faculty_role=faculty_role,
            reviewer_type=reviewer_type,
            student_name=student_name,
            reg_no=reg_no,
            batch=batch,
            review_number=2,
            regulations=regulations,
            department=department,
            semester=semester,
            course_code=course_code,
            company_guide_name=company_guide_name,
            internal_guide_name=faculty_name,
            criteria_1=criteria_1,
            criteria_2=criteria_2,
            criteria_3=criteria_3,
            criteria_4=criteria_4,
            criteria_5=criteria_5,
            criteria_6=criteria_6,
            criteria_7=criteria_7,
            criteria_8=criteria_8,
            criteria_9=criteria_9,
            criteria_10=criteria_10,
            total=total,
        )
        return redirect('review2_markentry')

    # For GET requests, handle the display logic
    projects_list = Project.objects.filter(department=department)
    
    # Check if faculty is assigned as a reviewer
    assigned_as_reviewer = assignreviewers.objects.filter(
        department=department
    ).filter(
        Q(reviewer1=name) | Q(reviewer2=name) | Q(reviewer3=name)
    ).exists()

    # Check if faculty is assigned as a guide
    assigned_as_guide = Project.objects.filter(
        department=department,
        internal_guide_name=name
    ).exists()

    # Get list of students where marks haven't been entered yet
    marked_as_guide = review_marks_master.objects.filter(
        faculty_name=name,
        reviewer_type='Guide',
        review_number=2
    ).values_list('reg_no', flat=True)

    marked_as_reviewer = review_marks_master.objects.filter(
        faculty_name=name,
        reviewer_type='Reviewer',
        review_number=2
    ).values_list('reg_no', flat=True)

    # Get students for guide role
    guide_students = Project.objects.filter(
        department=department,
        internal_guide_name=name
    ).exclude(reg_no__in=marked_as_guide)

    # Get students for reviewer role
    if assigned_as_reviewer:
        reviewer_students = Project.objects.filter(
            department=department,
            batch__in=assignreviewers.objects.filter(
                Q(reviewer1=name) | Q(reviewer2=name) | Q(reviewer3=name)
            ).values_list('batch', flat=True)
        ).exclude(reg_no__in=marked_as_reviewer)
    else:
        reviewer_students = Project.objects.none()

    return render(request, "faculty/review/review2_markentry.html", {
        "projects": projects_list,
        'role': role,
        'department': department,
        'name': name,
        'guide_students': guide_students,
        'reviewer_students': reviewer_students,
        'is_guide': assigned_as_guide,
        'is_reviewer': assigned_as_reviewer
    })

def review3_markentry(request):
    role = request.session.get('role')
    department = request.session.get('department')
    name = request.session.get('name')

    if request.method == "POST":
        faculty_name = name
        faculty_role = role
        student_name = request.POST.get('student_name')
        reg_no = request.POST.get('reg_no')
        semester_value = request.POST.get('semester')
        try:
            semester = int(semester_value) if semester_value not in [None, ''] else 0
        except ValueError:
            semester = 0
        
        course_code = request.POST.get('course_code')
        course_title = request.POST.get('course_title')
        reviewer_type = request.POST.get('reviewer_type')
        
        # Get marks for each criteria
        criteria_1 = int(request.POST.get('criteria_1', 0))
        criteria_2 = int(request.POST.get('criteria_2', 0))
        criteria_3 = int(request.POST.get('criteria_3', 0))
        criteria_4 = int(request.POST.get('criteria_4', 0))
        criteria_5 = int(request.POST.get('criteria_5', 0))
        criteria_6 = int(request.POST.get('criteria_6', 0))
        criteria_7 = int(request.POST.get('criteria_7', 0))
        criteria_8 = int(request.POST.get('criteria_8', 0))
        criteria_9 = int(request.POST.get('criteria_9', 0))
        criteria_10 = int(request.POST.get('criteria_10', 0))
        
        total = (criteria_1 + criteria_2 + criteria_3 + criteria_4 + criteria_5 +
                criteria_6 + criteria_7 + criteria_8 + criteria_9 + criteria_10)
        
        assign_record = assignreviewers.objects.filter(coursecode=course_code, department=department).first()
        if assign_record:
            batch = assign_record.batch
            regulations = assign_record.regulation  
            company_guide_name = assign_record.company_name
        else:
            batch = ""
            regulations = ""
            company_guide_name = ""

        # Create the review_marks_master record
        review_marks_master.objects.create(
            faculty_name=faculty_name,
            faculty_role=faculty_role,
            reviewer_type=reviewer_type,
            student_name=student_name,
            reg_no=reg_no,
            batch=batch,
            review_number=3,
            regulations=regulations,
            department=department,
            semester=semester,
            course_code=course_code,
            company_guide_name=company_guide_name,
            internal_guide_name=faculty_name,
            criteria_1=criteria_1,
            criteria_2=criteria_2,
            criteria_3=criteria_3,
            criteria_4=criteria_4,
            criteria_5=criteria_5,
            criteria_6=criteria_6,
            criteria_7=criteria_7,
            criteria_8=criteria_8,
            criteria_9=criteria_9,
            criteria_10=criteria_10,
            total=total,
        )
        return redirect('review3_markentry')

    # For GET requests, handle the display logic
    projects_list = Project.objects.filter(department=department)
    print(projects_list)
    
    # Check if faculty is assigned as a reviewer
    assigned_as_reviewer = assignreviewers.objects.filter(
        department=department
    ).filter(
        Q(reviewer1=name) | Q(reviewer2=name) | Q(reviewer3=name)
    ).exists()

    # Check if faculty is assigned as a guide
    assigned_as_guide = Project.objects.filter(
        department=department,
        internal_guide_name=name
    ).exists()

    # Get list of students where marks haven't been entered yet
    marked_as_guide = review_marks_master.objects.filter(
        faculty_name=name,
        reviewer_type='Guide',
        review_number=3
    ).values_list('reg_no', flat=True)

    marked_as_reviewer = review_marks_master.objects.filter(
        faculty_name=name,
        reviewer_type='Reviewer',
        review_number=3
    ).values_list('reg_no', flat=True)

    # Get students for guide role
    guide_students = Project.objects.filter(
        department=department,
        internal_guide_name=name
    ).exclude(reg_no__in=marked_as_guide)

    # Get students for reviewer role
    if assigned_as_reviewer:
        reviewer_students = Project.objects.filter(
            department=department,
            batch__in=assignreviewers.objects.filter(
                Q(reviewer1=name) | Q(reviewer2=name) | Q(reviewer3=name)
            ).values_list('batch', flat=True)
        ).exclude(reg_no__in=marked_as_reviewer)
    else:
        reviewer_students = Project.objects.none()

    return render(request, "faculty/review/review3_markentry.html", {
        "projects": projects_list,
        'role': role,
        'department': department,
        'name': name,
        'guide_students': guide_students,
        'reviewer_students': reviewer_students,
        'is_guide': assigned_as_guide,
        'is_reviewer': assigned_as_reviewer
    })




#↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑ hod part ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
#↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓faculty mark entry part↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓

def faculty_dashboard(request):
    role = request.session.get('role')
    department = request.session.get('department')
    name = request.session.get('name')
    print(department)
    # Get all projects for the department
    projects_list = Project.objects.filter(department=department)

    # Fetch only projects that belong to the faculty's department
    projects = Project.objects.filter(department=department)

    # Pass session data to the template
    context = {
        'projects_list': projects_list,
        'user_id': request.session.get('user_id'),
        'role': request.session.get('role'),
        'department': request.session.get('department'),
        'name': request.session.get('name'),
    }
    print(context)

    return render(request, 'faculty/faculty_dashboard.html', context)



def faculty_review1_markentry(request):
    role = request.session.get('role')
    department = request.session.get('department')
    name = request.session.get('name')
    
    if request.method == "POST":
        faculty_name = name
        faculty_role = role
        student_name = request.POST.get('student_name')
        reg_no = request.POST.get('reg_no')
        semester_value = request.POST.get('semester')
        try:
            semester = int(semester_value) if semester_value not in [None, ''] else 0
        except ValueError:
            semester = 0
        
        course_code = request.POST.get('course_code')
        course_title = request.POST.get('course_title')
        reviewer_type = request.POST.get('reviewer_type')
        
        # Get marks for each criteria
        criteria_1 = int(request.POST.get('criteria_1', 0))
        criteria_2 = int(request.POST.get('criteria_2', 0))
        criteria_3 = int(request.POST.get('criteria_3', 0))
        criteria_4 = int(request.POST.get('criteria_4', 0))
        criteria_5 = int(request.POST.get('criteria_5', 0))
        criteria_6 = int(request.POST.get('criteria_6', 0))
        criteria_7 = int(request.POST.get('criteria_7', 0))
        criteria_8 = int(request.POST.get('criteria_8', 0))
        criteria_9 = int(request.POST.get('criteria_9', 0))
        criteria_10 = int(request.POST.get('criteria_10', 0))
        
        total = (criteria_1 + criteria_2 + criteria_3 + criteria_4 + criteria_5 +
                criteria_6 + criteria_7 + criteria_8 + criteria_9 + criteria_10)
        
        assign_record = assignreviewers.objects.filter(coursecode=course_code, department=department).first()
        if assign_record:
            batch = assign_record.batch
            regulations = assign_record.regulation  
            company_guide_name = assign_record.company_name
        else:
            batch = ""
            regulations = ""
            company_guide_name = ""

        # Create the review_marks_master record
        review_marks_master.objects.create(
            faculty_name=faculty_name,
            faculty_role=faculty_role,
            reviewer_type=reviewer_type,
            student_name=student_name,
            reg_no=reg_no,
            batch=batch,
            review_number=1,
            regulations=regulations,
            department=department,
            semester=semester,
            course_code=course_code,
            company_guide_name=company_guide_name,
            internal_guide_name=faculty_name,
            criteria_1=criteria_1,
            criteria_2=criteria_2,
            criteria_3=criteria_3,
            criteria_4=criteria_4,
            criteria_5=criteria_5,
            criteria_6=criteria_6,
            criteria_7=criteria_7,
            criteria_8=criteria_8,
            criteria_9=criteria_9,
            criteria_10=criteria_10,
            total=total,
        )
        
        from django.http import JsonResponse
        return JsonResponse({'status': 'success'})

    # For GET requests
    projects_list = Project.objects.filter(department=department)

    # Check if the faculty is a reviewer in the assignreviewers table
    assigned_projects = assignreviewers.objects.filter(
        department=department
    ).filter(
        Q(reviewer1=name) | Q(reviewer2=name) | Q(reviewer3=name)
    )

    is_reviewer = assigned_projects.exists()  # True if faculty is a reviewer

    # If faculty is a reviewer, fetch projects assigned to them
    if is_reviewer:
        filtered_students_list = Project.objects.filter(
            department=department,
            batch__in=assigned_projects.values_list('batch', flat=True)
        )
    else:
        # If faculty is NOT a reviewer, fetch projects where they are the internal guide
        filtered_students_list = Project.objects.filter(
            department=department,
            internal_guide_name=name
        )

    return render(request, "faculty/review/faculty_review1_markentry.html", {
        'role': role,
        'department': department,
        'name': name,
        'projects_list': projects_list,
        'filtered_students_list': filtered_students_list,
        'is_reviewer': is_reviewer,
    })


def faculty_review2_markentry(request):
    role = request.session.get('role')
    department = request.session.get('department')
    name = request.session.get('name')
    print(name)

    projects_list = Project.objects.filter(department=department)
    print(projects_list)

    # Check if the faculty is a reviewer in the assignreviewers table
    assigned_projects = assignreviewers.objects.filter(
        department=department
    ).filter(
        Q(reviewer1=name) | Q(reviewer2=name) | Q(reviewer3=name)
    )

    is_reviewer = assigned_projects.exists()  # True if faculty is a reviewer

    # If faculty is a reviewer, fetch projects assigned to them
    if is_reviewer:
        filtered_students_list = Project.objects.filter(
            department=department,
            batch__in=assigned_projects.values_list('batch', flat=True)
        )
    else:
        # If faculty is NOT a reviewer, fetch projects where they are the internal guide
        filtered_students_list = Project.objects.filter(
            department=department,
            internal_guide_name=name
        )

    print("Is Reviewer:", is_reviewer)
    print("Filtered Students List:", filtered_students_list)

    return render(request, "faculty/review/faculty_review2_markentry.html", {
        'role': role,
        'department': department,
        'name': name,
        'projects_list': projects_list,
        'filtered_students_list': filtered_students_list,
        'is_reviewer': is_reviewer,  # Pass True or False
    })





from django.db.models import Q

def faculty_review3_markentry(request):
    role = request.session.get('role')
    department = request.session.get('department')
    name = request.session.get('name')
    print(name)

    projects_list = Project.objects.filter(department=department)
    print(projects_list)

    # Check if the faculty is a reviewer in the assignreviewers table
    assigned_projects = assignreviewers.objects.filter(
        department=department
    ).filter(
        Q(reviewer1=name) | Q(reviewer2=name) | Q(reviewer3=name)
    )

    is_reviewer = assigned_projects.exists()  # True if faculty is a reviewer

    # If faculty is a reviewer, fetch projects assigned to them
    if is_reviewer:
        filtered_students_list = Project.objects.filter(
            department=department,
            batch__in=assigned_projects.values_list('batch', flat=True)
        )
    else:
        # If faculty is NOT a reviewer, fetch projects where they are the internal guide
        filtered_students_list = Project.objects.filter(
            department=department,
            internal_guide_name=name
        )

    print("Is Reviewer:", is_reviewer)
    print("Filtered Students List:", filtered_students_list)

    return render(request, "faculty/review/faculty_review3_markentry.html", {
        'role': role,
        'department': department,
        'name': name,
        'projects_list': projects_list,
        'filtered_students_list': filtered_students_list,
        'is_reviewer': is_reviewer,  # Pass True or False
    })


def admin_portal(request):
    return(request,"e-approval/page.html")
