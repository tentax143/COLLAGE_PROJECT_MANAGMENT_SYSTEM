from django.shortcuts import render
from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse
import os
from django.conf import settings
from .models import Student,User,faculty_master,Project,assignreviewers,regulation_master,Student_cgpa,Course,review_marks_master, final_outcome
from datetime import datetime
from django.contrib import messages
import hashlib
from django.db import connections
from django.http import JsonResponse
import pandas as pd
from io import BytesIO
from django.db.models import Count

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
    faculty_list = User.objects.using('rit_e_approval').filter(Department=department).distinct()
    

    print(faculty_list)
    if request.method == 'POST':
        Project_title = request.POST.get('title')
        domain = request.POST.get('domain')
        project_type = request.POST.get('type')
        print(project_type)
    
        if project_type == 'internal':
            internal_guide_name = request.POST.get('internal_guide_name')
            print(internal_guide_name)
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
#↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓#faculty part↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓



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
            elif user.role == 'Principal':
                return redirect('principal_dashboard')
            elif user.role == 'Staff':
                return redirect('faculty_dashboard')
        else:
            print("Authentication failed! Incorrect password.")
            return render(request, 'faculty/faculty_login.html', {'error': 'Invalid credentials!'})
    
    return render(request, 'faculty/faculty_login.html')





#↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ hod part ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓


from django.db.models import Q
from datetime import datetime
def hod_dashbord(request):
    role = request.session.get('role')
    department = request.session.get('department')
    name = request.session.get('name')

    batch = int(datetime.now().year)
    current_batch = f"{batch-4}-{str(batch)[2:]}"
    project_batch = f"{batch-4}-{str(batch)}"
    
        # Get all projects for the department from the default database
    projects_list = Project.objects.filter(department=department, batch=project_batch)
    total_projects_submitted = projects_list.count()

    # Get all students from placement portal database
    all_students = Student_cgpa.objects.using('rit_cgpatrack').filter(batch=current_batch)
    total_students = all_students.count()

    # Calculate submission percentage
    submission_percentage = round((total_projects_submitted / total_students) * 100) if total_students > 0 else 0
    
    # Get all students who have marks awarded
    total_marks_awarded = review_marks_master.objects.filter(
        department=department
    ).values('reg_no').distinct().count()

    # Calculate review completion percentage
    review_percentage = round((total_marks_awarded / total_projects_submitted) * 100) if total_projects_submitted > 0 else 0

    # Get students who haven't submitted projects
    submitted_student_regnos = list(projects_list.values_list('reg_no', flat=True))
    students_without_projects = Student_cgpa.objects.using('rit_cgpatrack').exclude(reg_no__in=submitted_student_regnos).filter(batch=current_batch)
    pending_submissions = students_without_projects.count()

    # Calculate project type distribution
    internal_projects = projects_list.filter(project_type='internal').count()
    external_projects = projects_list.filter(project_type='external').count()
    research_projects = projects_list.filter(project_type='research').count()
    
    # Calculate percentages for project types
    internal_percentage = round((internal_projects / total_projects_submitted) * 100) if total_projects_submitted > 0 else 0
    external_percentage = round((external_projects / total_projects_submitted) * 100) if total_projects_submitted > 0 else 0
    research_percentage = round((research_projects / total_projects_submitted) * 100) if total_projects_submitted > 0 else 0
    
    # Calculate project statuses based on achieved field and review marks
    completed = projects_list.filter(achieved='yes').count()
    in_progress = total_projects_submitted - completed
    
    # Calculate pending reviews
    pending_reviews = total_projects_submitted - total_marks_awarded

    context = {
        'role': role,
        'department': department,
        'name': name,
        'projects_list': projects_list,
        'total_students': total_students,
        'total_projects_submitted': total_projects_submitted,
        'total_marks_awarded': total_marks_awarded,
        'pending_submissions': pending_submissions,
        'students_without_projects': students_without_projects,
        'submission_percentage': submission_percentage,
        'review_percentage': review_percentage,
        'internal_percentage': internal_percentage,
        'external_percentage': external_percentage,
        'research_percentage': research_percentage,
        'in_progress': in_progress,
        'completed': completed,
        'pending_reviews': pending_reviews
    }
    
    return render(request, "faculty/hod_dashbord.html", context)

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

    # Get current reviewers for this department
    current_reviewers = assignreviewers.objects.filter(
        department=department,
        review_type="Review 1"
    ).first()

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

        # Update or create the assignreviewers record
        assignreviewers.objects.update_or_create(
            department=department,
            review_type=review_type,
            defaults={
                'reviewer1': reviewer1,
                'reviewer2': reviewer2,
                'reviewer3': reviewer3,
                'regulation': regulation_selected,
                'coursecode': course_code,
                'coursename': course_name,
                'batch': batch,
                'sem': sem,
            }
        )

        messages.success(request, "Reviewers updated successfully!")
        return redirect("review1")

    return render(request, "faculty/review/review1.html", {
        "projects_list": projects_list,
        "role": role,
        "department": department,
        "name": name,
        "faculty_list": faculty_list,
        "regulation": regulation,
        "courses": courses,
        "current_reviewers": current_reviewers,
    })



def review2(request):
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

    # Get current reviewers for this department
    current_reviewers = assignreviewers.objects.filter(
        department=department,
        review_type="Review 2"
    ).first()
    
    if request.method == "POST":
        review_type = "Review 2"
        reviewer1_id = request.POST.get("reviewer1")
        reviewer2_id = request.POST.get("reviewer2")
        reviewer3_id = request.POST.get("reviewer3")
        regulation_selected = request.POST.get("regulation")

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

        # Update or create the assignreviewers record
        assignreviewers.objects.update_or_create(
            department=department,
            review_type=review_type,
            defaults={
                'reviewer1': reviewer1_name,
                'reviewer2': reviewer2_name,
                'reviewer3': reviewer3_name,
                'regulation': regulation_selected,
                'coursecode': course_code,
                'coursename': course_name,
                'batch': batch,
                'sem': sem,
            }
        )

        messages.success(request, "Reviewers updated successfully!")
        return redirect("review2")

    return render(request, "faculty/review/review2.html", {
        "projects_list": projects_list,
        "role": role,
        "department": department,
        "name": name,
        "faculty_list": faculty_list,
        "regulation": regulation,
        "courses": courses,
        "current_reviewers": current_reviewers,
    })

def review3(request):
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

    # Get current reviewers for this department
    current_reviewers = assignreviewers.objects.filter(
        department=department,
        review_type="Review 3"
    ).first()

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

        # Update or create the assignreviewers record
        assignreviewers.objects.update_or_create(
            department=department,
            review_type=review_type,
            defaults={
                'reviewer1': reviewer1_name,
                'reviewer2': reviewer2_name,
                'reviewer3': reviewer3_name,
                'regulation': regulation_selected,
                'coursecode': course_code,
                'coursename': course_name,
                'batch': batch,
                'sem': sem,
                'expname': industrial_expert_name,
                'company_name': company_name,
                'desegnation': designation
            }
        )

        messages.success(request, "Reviewers updated successfully!")
        return redirect("review3")

    return render(request, "faculty/review/review3.html", {
        "projects_list": projects_list,
        "role": role,
        "department": department,
        "name": name,
        "faculty_list": faculty_list,
        "regulation": regulation,
        "courses": courses,
        "current_reviewers": current_reviewers,
    })

from django.shortcuts import render, redirect
from .models import Project, assignreviewers, User

from django.db.models import Q

def guide_alocation(request):
    role = request.session.get('role')
    department1 = request.session.get('department')
    name = request.session.get('name')

    faculty_list = User.objects.using('rit_e_approval').filter(Department=department1)
    
    # Get all internal projects and external projects without guides
    projects = Project.objects.filter(
        department=department1
    ).filter(
        Q(project_type='internal') |  # Show all internal projects
        (Q(project_type='external') & (Q(internal_guide_name__isnull=True) | Q(internal_guide_name='')))  # Show only external projects without guides
    )

    if request.method == "POST":
        student_ids = request.POST.getlist("student_ids")
        faculty_id = request.POST.get("faculty_id")

        if not student_ids:
            messages.error(request, "Please select at least one student.")
            return redirect("guide_alocation")

        if not faculty_id:
            messages.error(request, "Please select a faculty member to assign as guide.")
            return redirect("guide_alocation")

        try:
            faculty = User.objects.using('rit_e_approval').get(id=faculty_id)
            
            # Update the selected projects with the new guide
            updated_count = Project.objects.filter(id__in=student_ids).update(
                    internal_guide_name=faculty.Name
                )
            
            if updated_count > 0:
                messages.success(
                    request, 
                    f"Successfully assigned {faculty.Name} as guide to {updated_count} project(s)."
                )
            else:
                messages.warning(request, "No projects were updated.")
                
        except User.DoesNotExist:
            messages.error(request, "Selected faculty member not found.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

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
    
    # Check if HOD is assigned as a reviewer in assignreviewers table
    is_reviewer = assignreviewers.objects.filter(
        department=department,
        review_type="Review 1"
    ).filter(
        Q(reviewer1=name) | Q(reviewer2=name) | Q(reviewer3=name)
    ).exists()

    # Get students whose marks have already been entered for Review 1 by either guide or reviewer
    students_with_guide_marks = review_marks_master.objects.filter(
        department=department,
        review_number=1,
        reviewer_type='Guide'
    ).values_list('reg_no', flat=True)

    students_with_reviewer_marks = review_marks_master.objects.filter(
        department=department,
        review_number=1,
        reviewer_type='Reviewer'
    ).values_list('reg_no', flat=True)

    # Get students where HOD is the internal guide
    guide_students = Project.objects.filter(
        department=department,
        internal_guide_name=name
    ).exclude(reg_no__in=students_with_guide_marks)

    # If HOD is a reviewer, get reviewer students
    if is_reviewer:
        reviewer_students = Project.objects.filter(
            department=department,
            batch__in=assignreviewers.objects.filter(
                department=department,
                review_type="Review 1"
            ).filter(
                Q(reviewer1=name) | Q(reviewer2=name) | Q(reviewer3=name)
            ).values_list('batch', flat=True)
        ).exclude(reg_no__in=students_with_reviewer_marks)
    else:
        reviewer_students = Project.objects.none()

    return render(request, "faculty/review/review1_markentry.html", {
        "projects": projects_list,
        'role': role,
        'department': department,
        'name': name,
        'guide_students': guide_students,
        'reviewer_students': reviewer_students,
        'is_reviewer': is_reviewer
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
    
    # Check if HOD is assigned as a reviewer in assignreviewers table
    is_reviewer = assignreviewers.objects.filter(
        department=department,
        review_type="Review 2"
    ).filter(
        Q(reviewer1=name) | Q(reviewer2=name) | Q(reviewer3=name)
    ).exists()

    # Get students whose marks have already been entered for Review 2 by either guide or reviewer
    students_with_guide_marks = review_marks_master.objects.filter(
        department=department,
        review_number=2,
        reviewer_type='Guide'
    ).values_list('reg_no', flat=True)

    students_with_reviewer_marks = review_marks_master.objects.filter(
        department=department,
        review_number=2,
        reviewer_type='Reviewer'
    ).values_list('reg_no', flat=True)

    # Get students where HOD is the internal guide
    guide_students = Project.objects.filter(
        department=department,
        internal_guide_name=name
    ).exclude(reg_no__in=students_with_guide_marks)

    # If HOD is a reviewer, get reviewer students
    if is_reviewer:
        reviewer_students = Project.objects.filter(
            department=department,
            batch__in=assignreviewers.objects.filter(
                department=department,
                review_type="Review 2"
            ).filter(
                Q(reviewer1=name) | Q(reviewer2=name) | Q(reviewer3=name)
            ).values_list('batch', flat=True)
        ).exclude(reg_no__in=students_with_reviewer_marks)
    else:
        reviewer_students = Project.objects.none()

    return render(request, "faculty/review/review2_markentry.html", {
        "projects": projects_list,
        'role': role,
        'department': department,
        'name': name,
        'guide_students': guide_students,
        'reviewer_students': reviewer_students,
        'is_reviewer': is_reviewer
    })

def faculty_review3_markentry(request):
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
        
        return JsonResponse({'status': 'success'})

    # For GET requests
    projects_list = Project.objects.filter(department=department)

    # Check if the faculty is a reviewer for Review 3 specifically
    assigned_projects = assignreviewers.objects.filter(
        department=department,
        review_type="Review 3"  # Specifically check for Review 3
    ).filter(
        Q(reviewer1=name) | Q(reviewer2=name) | Q(reviewer3=name)
    )

    is_reviewer = assigned_projects.exists()  # True if faculty is a reviewer for Review 3

    # Get students whose marks have already been entered for Review 3 by either guide or reviewer
    students_with_guide_marks = review_marks_master.objects.filter(
        department=department,
        review_number=3,
        reviewer_type='Guide'
    ).values_list('reg_no', flat=True)

    students_with_reviewer_marks = review_marks_master.objects.filter(
        department=department,
        review_number=3,
        reviewer_type='Reviewer'
    ).values_list('reg_no', flat=True)

    # If faculty is a reviewer for Review 3, fetch projects assigned to them
    if is_reviewer:
        filtered_students_list = Project.objects.filter(
            department=department,
            batch__in=assigned_projects.values_list('batch', flat=True)
        ).exclude(reg_no__in=students_with_reviewer_marks)
    else:
        # If faculty is NOT a reviewer for Review 3, fetch projects where they are the internal guide
        filtered_students_list = Project.objects.filter(
            department=department,
            internal_guide_name=name
        ).exclude(reg_no__in=students_with_guide_marks)

    return render(request, 'faculty/review/faculty_review3_markentry.html', {
        'projects_list': filtered_students_list,
        'is_reviewer': is_reviewer,
        'guide_students': filtered_students_list,
        'role': role,
        'department': department,
        'name': name
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
    
    # Check if HOD is assigned as a reviewer in assignreviewers table
    is_reviewer = assignreviewers.objects.filter(
        department=department,
        review_type="Review 3"
    ).filter(
        Q(reviewer1=name) | Q(reviewer2=name) | Q(reviewer3=name)
    ).exists()

    # Get students whose marks have already been entered for Review 3 by either guide or reviewer
    students_with_guide_marks = review_marks_master.objects.filter(
        department=department,
        review_number=3,
        reviewer_type='Guide'
    ).values_list('reg_no', flat=True)

    students_with_reviewer_marks = review_marks_master.objects.filter(
        department=department,
        review_number=3,
        reviewer_type='Reviewer'
    ).values_list('reg_no', flat=True)

    # Get students where HOD is the internal guide
    guide_students = Project.objects.filter(
        department=department,
        internal_guide_name=name
    ).exclude(reg_no__in=students_with_guide_marks)

    # If HOD is a reviewer, get reviewer students
    if is_reviewer:
        reviewer_students = Project.objects.filter(
            department=department,
            batch__in=assignreviewers.objects.filter(
                department=department,
                review_type="Review 3"
            ).filter(
                Q(reviewer1=name) | Q(reviewer2=name) | Q(reviewer3=name)
            ).values_list('batch', flat=True)
        ).exclude(reg_no__in=students_with_reviewer_marks)
    else:
        reviewer_students = Project.objects.none()

    return render(request, "faculty/review/review3_markentry.html", {
        "projects": projects_list,
        'role': role,
        'department': department,
        'name': name,
        'guide_students': guide_students,
        'reviewer_students': reviewer_students,
        'is_reviewer': is_reviewer
    })

#↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑ hod part ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
#↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓faculty mark entry part↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓

def faculty_dashboard(request):
    role = request.session.get('role')
    department = request.session.get('department')
    name = request.session.get('name')
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
        
        return JsonResponse({'status': 'success'})

    # For GET requests
    projects_list = Project.objects.filter(department=department)
    print(f"Total projects in department: {projects_list.count()}")

    # Check if the faculty is a reviewer for Review 1 specifically
    assigned_projects = assignreviewers.objects.filter(
        department=department,
        review_type="Review 1"  # Specifically check for Review 1
    ).filter(
        Q(reviewer1=name) | Q(reviewer2=name) | Q(reviewer3=name)
    )
    print(f"Assigned projects for faculty {name}: {assigned_projects.count()}")

    is_reviewer = assigned_projects.exists()  # True if faculty is a reviewer for Review 1
    print(f"Is reviewer: {is_reviewer}")

    # Get students whose marks have already been entered for Review 1 by either guide or reviewer
    students_with_guide_marks = review_marks_master.objects.filter(
        department=department,
        review_number=1,
        reviewer_type='Guide'
    ).values_list('reg_no', flat=True)
    print(f"Students with guide marks: {len(students_with_guide_marks)}")

    students_with_reviewer_marks = review_marks_master.objects.filter(
        department=department,
        review_number=1,
        reviewer_type='Reviewer'
    ).values_list('reg_no', flat=True)
    print(f"Students with reviewer marks: {len(students_with_reviewer_marks)}")

    # Get students where faculty is the internal guide
    guide_students = Project.objects.filter(
        department=department,
        internal_guide_name=name
    ).exclude(reg_no__in=students_with_guide_marks)
    print(f"Guide students count: {guide_students.count()}")

    # If faculty is a reviewer, get reviewer students
    if is_reviewer:
        reviewer_students = Project.objects.filter(
            department=department,
            batch__in=assigned_projects.values_list('batch', flat=True)
        ).exclude(reg_no__in=students_with_reviewer_marks)
        print(f"Reviewer students count: {reviewer_students.count()}")
    else:
        reviewer_students = Project.objects.none()

    # Get all students for debugging
    all_students = Project.objects.filter(department=department)
    print(f"All students in department: {all_students.count()}")
    print(f"Faculty name: {name}")
    print(f"Department: {department}")

    return render(request, 'faculty/review/faculty_review1_markentry.html', {
        'projects_list': projects_list,
        'is_reviewer': is_reviewer,
        'guide_students': guide_students,
        'reviewer_students': reviewer_students,
        'role': role,
        'department': department,
        'name': name
    })


def faculty_review2_markentry(request):
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
        
        return JsonResponse({'status': 'success'})

    # For GET requests
    projects_list = Project.objects.filter(department=department)
    print(f"Total projects in department: {projects_list.count()}")

    # Check if the faculty is a reviewer for Review 2 specifically
    assigned_projects = assignreviewers.objects.filter(
        department=department,
        review_type="Review 2"  # Specifically check for Review 2
    ).filter(
        Q(reviewer1=name) | Q(reviewer2=name) | Q(reviewer3=name)
    )
    print(f"Assigned projects for faculty {name}: {assigned_projects.count()}")

    is_reviewer = assigned_projects.exists()  # True if faculty is a reviewer for Review 2
    print(f"Is reviewer: {is_reviewer}")

    # Get students whose marks have already been entered for Review 2 by either guide or reviewer
    students_with_guide_marks = review_marks_master.objects.filter(
        department=department,
        review_number=2,
        reviewer_type='Guide'
    ).values_list('reg_no', flat=True)
    print(f"Students with guide marks: {len(students_with_guide_marks)}")

    students_with_reviewer_marks = review_marks_master.objects.filter(
        department=department,
        review_number=2,
        reviewer_type='Reviewer'
    ).values_list('reg_no', flat=True)
    print(f"Students with reviewer marks: {len(students_with_reviewer_marks)}")

    # Get students where faculty is the internal guide
    guide_students = Project.objects.filter(
        department=department,
        internal_guide_name=name
    ).exclude(reg_no__in=students_with_guide_marks)
    print(f"Guide students count: {guide_students.count()}")

    # If faculty is a reviewer, get reviewer students
    if is_reviewer:
        reviewer_students = Project.objects.filter(
            department=department,
            batch__in=assigned_projects.values_list('batch', flat=True)
        ).exclude(reg_no__in=students_with_reviewer_marks)
        print(f"Reviewer students count: {reviewer_students.count()}")
    else:
        reviewer_students = Project.objects.none()

    # Get all students for debugging
    all_students = Project.objects.filter(department=department)
    print(f"All students in department: {all_students.count()}")
    print(f"Faculty name: {name}")
    print(f"Department: {department}")

    return render(request, 'faculty/review/faculty_review2_markentry.html', {
        'projects_list': projects_list,
        'is_reviewer': is_reviewer,
        'guide_students': guide_students,
        'reviewer_students': reviewer_students,
        'role': role,
        'department': department,
        'name': name
    })

def handle_uploaded_file(file, batch, department, reg_no):
    # Create directory structure: batch/department/reg_no/
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'outcome_certificates', str(batch), str(department), str(reg_no))

    # Create directories if they don't exist
    os.makedirs(upload_dir, exist_ok=True)

    # Generate unique filename using timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_extension = os.path.splitext(file.name)[1]
    filename = f'outcome_certificate_{timestamp}{file_extension}'

    # Full path for the file
    file_path = os.path.join(upload_dir, filename)

    # Save the file
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    # Return the relative path from MEDIA_ROOT
    return os.path.join('outcome_certificates', str(batch), str(department), str(reg_no), filename)

def final_outcome_entry(request):
    role = request.session.get('role')
    department = request.session.get('department')
    name = request.session.get('name')

    if request.method == "POST":
        form_type = request.POST.get('form_type')
        
        if form_type == 'both':
            try:
                print("Received POST data:", request.POST)
                print("Received FILES:", request.FILES)
                
                # Get the project
                project = Project.objects.get(
                    student_name=request.POST.get('student_name'),
                    reg_no=request.POST.get('reg_no'),
        department=department
                )
                
                # Handle file upload if present
                if 'outcome_certificate' in request.FILES:
                    file = request.FILES['outcome_certificate']
                    relative_file_path = handle_uploaded_file(file, project.batch, project.department, project.reg_no)
                    
                    # Update project model with file path
                    project.outcome_certificate = relative_file_path
                    print(f"Updated project.outcome_certificate with: {relative_file_path}")
                
                # Update Project model fields
                project.project_outcome_type = request.POST.get('project_outcome_type')
                project.outcome = request.POST.get('outcome')
                project.achieved = request.POST.get('achieved')
                
                print("Saving project model with data:", {
                    'project_outcome_type': project.project_outcome_type,
                    'outcome': project.outcome,
                    'achieved': project.achieved,
                    'outcome_certificate': project.outcome_certificate if 'outcome_certificate' in request.FILES else 'No new file'
                })
                
                project.save()
                print("Project model saved successfully")

                # Process date fields
                filed_date = None
                published_date = None
                granted_date = None
                
                try:
                    if request.POST.get('filed_date'):
                        filed_date = datetime.strptime(request.POST.get('filed_date'), '%Y-%m-%d').date()
                    if request.POST.get('published_date'):
                        published_date = datetime.strptime(request.POST.get('published_date'), '%Y-%m-%d').date()
                    if request.POST.get('granted_date'):
                        granted_date = datetime.strptime(request.POST.get('granted_date'), '%Y-%m-%d').date()
                except ValueError as e:
                    print(f"Date parsing error: {str(e)}")
                    return JsonResponse({'status': 'error', 'message': f'Invalid date format: {str(e)}'}, status=400)

                # Prepare data for final_outcome model
                final_outcome_data = {
                    'batch': project.batch,
                    'semester': project.semester,
                    'guide_name': project.internal_guide_name,
                    'project_title': project.title,
                    'outcome': request.POST.get('outcome'),
                    'web_url': request.POST.get('web_url') or None,
                    'journal_name': request.POST.get('journal_name') or None,
                    'volume': request.POST.get('volume') or None,
                    'page_no': request.POST.get('page_no') or None,
                    'doi': request.POST.get('doi') or None,
                    'impact_factor': request.POST.get('impact_factor') or None,
                    'filed_date': filed_date,
                    'published_date': published_date,
                    'granted_date': granted_date,
                    'patent_web_url': request.POST.get('patent_web_url') or None,
                    'filed_name': request.POST.get('field_name') or None,
                    'patent_type': request.POST.get('patent_type') or None,
                    'inventor_name': request.POST.get('inventor_name') or None,
                    'patent_number': request.POST.get('patent_number') or None
                }

                if 'outcome_certificate' in request.FILES:
                    final_outcome_data['outcome_certificate'] = relative_file_path

                print("Creating/updating final_outcome with data:", final_outcome_data)

                # Create/Update final_outcome model
                final_outcome_obj, created = final_outcome.objects.update_or_create(
                    reg_no=request.POST.get('reg_no'),
                    defaults=final_outcome_data
                )

                print(f"final_outcome model {'created' if created else 'updated'} successfully")
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Outcome details saved successfully',
                    'created': created
                })

            except Project.DoesNotExist:
                print("Project not found error")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Project not found for the given student name and registration number'
                }, status=404)
            except Exception as e:
                print(f"Error saving outcome: {str(e)}")
                import traceback
                print("Full traceback:", traceback.format_exc())
                return JsonResponse({
                    'status': 'error',
                    'message': f'Error saving outcome: {str(e)}',
                    'details': traceback.format_exc()
                }, status=500)

    # Get all projects for the department
    projects_list = Project.objects.filter(department=department)

    # Get students assigned to the current faculty as internal guide
    filtered_students_list = Project.objects.filter(
            department=department,
            internal_guide_name=name
        )

    context = {
        'projects_list': projects_list,
        'role': role,
        'department': department,
        'name': name,
        'filtered_students_list': filtered_students_list,
    }

    return render(request, 'faculty/review/final_outcome_entry.html', context)

def filter(request):
    role = request.session.get('role')
    department = request.session.get('department')
    name = request.session.get('name')
    
    # Get filter parameters
    selected_batch = request.GET.get('batch')
    selected_outcome_type = request.GET.get('outcome_type')
    selected_achieved = request.GET.get('achieved')
    
    # Base queryset for the department
    projects = Project.objects.filter(department=department)
    
    # Apply filters if selected
    if selected_batch:
        projects = projects.filter(batch=selected_batch)
    if selected_outcome_type:
        projects = projects.filter(project_outcome_type=selected_outcome_type)
    if selected_achieved:
        projects = projects.filter(achieved=selected_achieved)
    
    # Get unique values for filter dropdowns
    available_batches = Project.objects.filter(department=department).values_list('batch', flat=True).distinct()
    available_outcome_types = Project.objects.filter(department=department).values_list('project_outcome_type', flat=True).distinct()
    available_achieved_statuses = Project.objects.filter(department=department).values_list('achieved', flat=True).distinct()
    
    # Count projects by outcome type
    total_application_projects = projects.filter(project_outcome_type='Application').count()
    total_research_projects = projects.filter(project_outcome_type='Research').count()
    total_patent_projects = projects.filter(project_outcome_type='Patent').count()
    total_product_projects = projects.filter(project_outcome_type='Product').count()
    total_students = projects.count()
    no_count = total_students - (total_application_projects + total_research_projects + total_patent_projects + total_product_projects)
    
    context = {
        'projects': projects,
        'total_students': total_students,
        'total_application_projects': total_application_projects,
        'total_research_projects': total_research_projects,
        'total_patent_projects': total_patent_projects,
        'total_product_projects': total_product_projects,
        'no_count': no_count,
        'role': role,
        'department': department,
        'name': name,
        'available_batches': available_batches,
        'available_outcome_types': available_outcome_types,
        'available_achieved_statuses': available_achieved_statuses,
        'selected_batch': selected_batch,
        'selected_outcome_type': selected_outcome_type,
        'selected_achieved': selected_achieved,
    }
    return render(request, "faculty/filter.html", context)

def admin_portal(request):
    return(request,"e-approval/page.html")


def principal_dashboard(request):
    role = request.session.get('role')
    name = request.session.get('name')
    batch = int(datetime.now().year)
    current_batch = f"{batch-4}-{str(batch)[2:]}"
    project_batch = f"{batch-4}-{str(batch)}"
    # Get filter parameters
    selected_department = request.GET.get('department')  # Default: Show all departments
    selected_batch = request.GET.get('batch')
    selected_outcome_type = request.GET.get('outcome_type')
    selected_achieved = request.GET.get('achieved')
    all_students = Student_cgpa.objects.using('rit_cgpatrack').filter(batch=current_batch)
    total_students = all_students.count()

    # Base queryset: Initially fetch all departments' data
    projects = Project.objects.all()

    # Count total students per department (initial state)
    department_wise_counts = (
        projects.values('department')
        .annotate(total_students=Count('id'))
        .order_by('department')
    )

    # Apply department filter dynamically
    if selected_department:
        projects = projects.filter(department=selected_department)
        p_1=projects.count()
        print(p_1)

    # Apply additional filters
    if selected_batch:
        projects = projects.filter(batch=selected_batch)
    if selected_outcome_type:
        projects = projects.filter(project_outcome_type=selected_outcome_type)
    if selected_achieved:
        projects = projects.filter(achieved=selected_achieved)

    # Get unique values for filter dropdowns
    available_departments = Project.objects.values_list('department', flat=True).distinct()
    available_batches = Project.objects.filter(department=selected_department).values_list('batch', flat=True).distinct() if selected_department else Project.objects.values_list('batch', flat=True).distinct()
    available_outcome_types = Project.objects.filter(department=selected_department).values_list('project_outcome_type', flat=True).distinct() if selected_department else Project.objects.values_list('project_outcome_type', flat=True).distinct()
    available_achieved_statuses = Project.objects.filter(department=selected_department).values_list('achieved', flat=True).distinct() if selected_department else Project.objects.values_list('achieved', flat=True).distinct()

    # Count projects by outcome type (Based on current filters)
    total_application_projects = projects.filter(project_outcome_type='Application').count()
    total_research_projects = projects.filter(project_outcome_type='Research').count()
    total_patent_projects = projects.filter(project_outcome_type='Patent').count()
    total_product_projects = projects.filter(project_outcome_type='Product').count()
    all_students = Student_cgpa.objects.using('rit_cgpatrack').filter(batch=current_batch)
    total_students = all_students.count()

    no_count = total_students - (total_application_projects + total_research_projects + total_patent_projects + total_product_projects)

    context = {
        'projects': projects,
        'total_students': total_students,
        'total_application_projects': total_application_projects,
        'total_research_projects': total_research_projects,
        'total_patent_projects': total_patent_projects,
        'total_product_projects': total_product_projects,
        'no_count': no_count,
        'role': role,
        'name': name,
        'available_departments': available_departments,  # List of all departments
        'available_batches': available_batches,
        'available_outcome_types': available_outcome_types,
        'available_achieved_statuses': available_achieved_statuses,
        'selected_department': selected_department,  # Current department selection
        'selected_batch': selected_batch,
        'selected_outcome_type': selected_outcome_type,
        'selected_achieved': selected_achieved,
        'department_wise_counts': department_wise_counts,  # Initial department-wise counts
    }
    
    return render(request, "faculty/principal_dashboard.html", context)

def criteria_analysis(request):
    role = request.session.get('role')
    name = request.session.get('name')
    
    # Get selected department from request, default to user's department if not specified
    selected_department = request.GET.get('department', request.session.get('department'))
    
    # Get all available departments for the dropdown
    available_departments = Project.objects.values_list('department', flat=True).distinct()
    
    # Filter projects based on selected department
    projects = Project.objects.filter(department=selected_department)
    
    # Count projects for different outcomes
    projects_1 = projects.filter(achieved="Yes", outcome="National Conference").count()
    projects_2 = projects.filter(achieved="Yes", outcome="International Conference").count()
    projects_3 = projects.filter(achieved="Yes", outcome="Scopus").count()
    projects_4 = projects.filter(achieved="Yes", outcome="SCIE").count()
    projects_5 = projects.filter(achieved="Yes", outcome="SCI").count()
    projects_6 = projects.filter(achieved="Yes", outcome="UGC").count()
    projects_7 = projects.filter(achieved="Yes", outcome="Others").count()
    
    # Calculate total projects for percentage calculations
    total_projects = projects_1 + projects_2 + projects_3 + projects_4 + projects_5 + projects_6 + projects_7
    
    # Calculate percentages
    percentages = {
        'national_conf': round((projects_1 / total_projects * 100) if total_projects > 0 else 0, 2),
        'international_conf': round((projects_2 / total_projects * 100) if total_projects > 0 else 0, 2),
        'scopus': round((projects_3 / total_projects * 100) if total_projects > 0 else 0, 2),
        'scie': round((projects_4 / total_projects * 100) if total_projects > 0 else 0, 2),
        'sci': round((projects_5 / total_projects * 100) if total_projects > 0 else 0, 2),
        'ugc': round((projects_6 / total_projects * 100) if total_projects > 0 else 0, 2),
        'others': round((projects_7 / total_projects * 100) if total_projects > 0 else 0, 2)
    }
    
    return render(request, "faculty/criteria_analysis.html", {
        'role': role,
        'name': name,
        'selected_department': selected_department,
        'available_departments': available_departments,
        'projects_1': projects_1,
        'projects_2': projects_2,
        'projects_3': projects_3,
        'projects_4': projects_4,
        'projects_5': projects_5,
        'projects_6': projects_6,
        'projects_7': projects_7,
        'total_projects': total_projects,
        'percentages': percentages,
    })

def export_to_excel(request):
    department = request.session.get('department')
    
    # Get all projects for the department
    projects = Project.objects.filter(department=department)
    
    # Create lists to store the data
    data = []
    
    for project in projects:
        # Try to get corresponding final_outcome record
        try:
            outcome = final_outcome.objects.get(reg_no=project.reg_no)
            
            # Combine data from both models
            row = {
                'Registration Number': project.reg_no,
                'Student Name': project.student_name,
                'Department': project.department,
                'Batch': project.batch,
                'Project Title': project.title,
                'Project Type': project.project_type,
                'Internal Guide': project.internal_guide_name,
                'Project Outcome Type': project.project_outcome_type,
                'Outcome': project.outcome,
                'Achieved': project.achieved,
                
                # Final Outcome specific fields
                'Journal Name': outcome.journal_name,
                'Volume': outcome.volume,
                'Page Number': outcome.page_no,
                'DOI': outcome.doi,
                'Impact Factor': outcome.impact_factor,
                'Web URL': outcome.web_url,
                
                # Patent specific fields
                'Patent Type': outcome.patent_type,
                'Filed Name': outcome.filed_name,
                'Inventor Name': outcome.inventor_name,
                'Patent Number': outcome.patent_number,
                'Filed Date': outcome.filed_date,
                'Published Date': outcome.published_date,
                'Granted Date': outcome.granted_date,
                'Patent Web URL': outcome.patent_web_url,
            }
            data.append(row)
        except final_outcome.DoesNotExist:
            # If no final_outcome record exists, just use project data
            row = {
                'Registration Number': project.reg_no,
                'Student Name': project.student_name,
                'Department': project.department,
                'Batch': project.batch,
                'Project Title': project.title,
                'Project Type': project.project_type,
                'Internal Guide': project.internal_guide_name,
                'Project Outcome Type': project.project_outcome_type,
                'Outcome': project.outcome,
                'Achieved': project.achieved,
                
                # Empty values for final_outcome fields
                'Journal Name': '',
                'Volume': '',
                'Page Number': '',
                'DOI': '',
                'Impact Factor': '',
                'Web URL': '',
                'Patent Type': '',
                'Filed Name': '',
                'Inventor Name': '',
                'Patent Number': '',
                'Filed Date': '',
                'Published Date': '',
                'Granted Date': '',
                'Patent Web URL': '',
            }
            data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    excel_file = BytesIO()
    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Project Outcomes', index=False)
        
        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Project Outcomes']
        
        # Add some formatting
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D3D3D3',
            'border': 1
        })
        
        # Format the header row
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 15)  # Set column width
    
    # Set up the response
    excel_file.seek(0)
    response = HttpResponse(
        excel_file.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=project_outcomes_{department}_{datetime.now().strftime("%Y%m%d")}.xlsx'
    
    return response

def download_certificate(request, reg_no):
    try:
        # Get the project
        project = Project.objects.get(reg_no=reg_no)
        
        if not project.outcome_certificate:
            print(f"No certificate found for reg_no: {reg_no}")
            return HttpResponse("No certificate found", status=404)
            
        # Get the directory path from the stored path
        stored_path = str(project.outcome_certificate)
        directory_path = os.path.dirname(os.path.join(settings.MEDIA_ROOT, stored_path))
        
        print(f"Looking for files in directory: {directory_path}")
        
        if not os.path.exists(directory_path):
            print(f"Directory does not exist: {directory_path}")
            return HttpResponse("Directory not found", status=404)
            
        # List all files in the directory
        files = os.listdir(directory_path)
        print(f"Files found in directory: {files}")
        
        # Find the most recent outcome certificate file
        matching_files = [f for f in files if f.startswith('outcome_certificate_')]
        if not matching_files:
            print("No matching files found")
            return HttpResponse("File not found", status=404)
            
        # Get the most recent file
        latest_file = max(matching_files, key=lambda x: os.path.getctime(os.path.join(directory_path, x)))
        file_path = os.path.join(directory_path, latest_file)
        
        print(f"Using file: {latest_file}")
        
        if not os.path.exists(file_path):
            print(f"File not found at path: {file_path}")
            return HttpResponse("File not found", status=404)
            
        # Open the file and create response
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{latest_file}"'
            return response
            
    except Project.DoesNotExist:
        print(f"Project not found for reg_no: {reg_no}")
        return HttpResponse("Project not found", status=404)
    except Exception as e:
        print(f"Error downloading file: {str(e)}")
        import traceback
        print("Full traceback:", traceback.format_exc())
        return HttpResponse(f"Error downloading file: {str(e)}", status=500)