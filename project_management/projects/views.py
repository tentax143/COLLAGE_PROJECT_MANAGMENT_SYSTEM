from django.shortcuts import render
from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse
import os
from django.conf import settings
from .models import Student,User,faculty_master,Project,assignreviewers,regulation_master,Student_cgpa,Course,review_marks_master, final_outcome,review_assasment_criteria_master
from datetime import datetime
from django.contrib import messages
import hashlib
from django.db import connections
from django.http import JsonResponse
import pandas as pd
from io import BytesIO
from django.db.models import Count
import json
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from traceback import format_exc

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


from django.http import JsonResponse
from .models import review_marks_master

def get_review_preview(request, review_number):
    try:
        department = request.session.get('department')
        
        # Get all review marks for this department
        if review_number == 4:
            # For all reviews, get data from all review numbers
            review_marks = review_marks_master.objects.filter(department=department)
        else:
            # For specific review, filter by review number
            review_marks = review_marks_master.objects.filter(
                department=department,
                review_number=review_number
            )
        
        # Group marks by student registration number
        student_data = {}
        
        for mark in review_marks:
            if mark.reg_no not in student_data:
                student_data[mark.reg_no] = {
                    'student_name': mark.student_name,
                    'reg_no': mark.reg_no,
                    'guide_total': None,
                    'guide_name': None,
                    'reviewer1_total': None,
                    'reviewer1_name': None,
                    'reviewer2_total': None,
                    'reviewer2_name': None,
                    'reviewer3_total': None,
                    'reviewer3_name': None,
                    'average': None
                }
            
            # Calculate total marks for this review
            criteria_marks = [
                mark.criteria_1 or 0,
                mark.criteria_2 or 0,
                mark.criteria_3 or 0,
                mark.criteria_4 or 0,
                mark.criteria_5 or 0,
                mark.criteria_6 or 0,
                mark.criteria_7 or 0,
                mark.criteria_8 or 0,
                mark.criteria_9 or 0,
                mark.criteria_10 or 0
            ]
            total_marks = sum(criteria_marks)
            
            # For all reviews (review_number == 4), update with highest marks
            if review_number == 4:
                if mark.reviewer_type == 'Guide':
                    if student_data[mark.reg_no]['guide_total'] is None or total_marks > student_data[mark.reg_no]['guide_total']:
                        student_data[mark.reg_no]['guide_total'] = total_marks
                        student_data[mark.reg_no]['guide_name'] = mark.faculty_name
                elif mark.reviewer_type == 'Reviewer 1':
                    if student_data[mark.reg_no]['reviewer1_total'] is None or total_marks > student_data[mark.reg_no]['reviewer1_total']:
                        student_data[mark.reg_no]['reviewer1_total'] = total_marks
                        student_data[mark.reg_no]['reviewer1_name'] = mark.faculty_name
                elif mark.reviewer_type == 'Reviewer 2':
                    if student_data[mark.reg_no]['reviewer2_total'] is None or total_marks > student_data[mark.reg_no]['reviewer2_total']:
                        student_data[mark.reg_no]['reviewer2_total'] = total_marks
                        student_data[mark.reg_no]['reviewer2_name'] = mark.faculty_name
                elif mark.reviewer_type == 'Reviewer 3':
                    if student_data[mark.reg_no]['reviewer3_total'] is None or total_marks > student_data[mark.reg_no]['reviewer3_total']:
                        student_data[mark.reg_no]['reviewer3_total'] = total_marks
                        student_data[mark.reg_no]['reviewer3_name'] = mark.faculty_name
            else:
                # For specific review, just update the marks
                if mark.reviewer_type == 'Guide':
                    student_data[mark.reg_no]['guide_total'] = total_marks
                    student_data[mark.reg_no]['guide_name'] = mark.faculty_name
                elif mark.reviewer_type == 'Reviewer 1':
                    student_data[mark.reg_no]['reviewer1_total'] = total_marks
                    student_data[mark.reg_no]['reviewer1_name'] = mark.faculty_name
                elif mark.reviewer_type == 'Reviewer 2':
                    student_data[mark.reg_no]['reviewer2_total'] = total_marks
                    student_data[mark.reg_no]['reviewer2_name'] = mark.faculty_name
                elif mark.reviewer_type == 'Reviewer 3':
                    student_data[mark.reg_no]['reviewer3_total'] = total_marks
                    student_data[mark.reg_no]['reviewer3_name'] = mark.faculty_name
        
        # Convert dictionary to list and calculate averages
        preview_data = []
        for student in student_data.values():
            # Calculate average from non-None values
            totals = [
                student['guide_total'],
                student['reviewer1_total'],
                student['reviewer2_total'],
                student['reviewer3_total']
            ]
            valid_totals = [t for t in totals if t is not None]
            average = sum(valid_totals) / len(valid_totals) if valid_totals else None
            
            student['average'] = round(average, 2) if average is not None else None
            preview_data.append(student)
        
        return JsonResponse(preview_data, safe=False)
        
    except Exception as e:
        print(f"Error in get_review_preview: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)



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
            'total': mark.total,
            'review1_comments': mark.review1_comments,
            'review2_comments': mark.review2_comments,
            'review3_comments': mark.review3_comments,
            'overall_comments': mark.overall_comments
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
            user = users[0]  # Select the second user if more than one exists
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





#↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ hod part ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓


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

    # Calculate department code from department name
    department_code = None
    if "ARTIFICIAL INTELLIGENCE AND DATA SCIENCE" in department:
        department_code = "243"
        cgpa_department = "B.TECH AD"
    elif "COMPUTER SCIENCE AND BUSINESS SYSTEM" in department:
        department_code = "107"
        cgpa_department = "B.TECH CSBS"
    elif "ELECTRONICS AND COMMUNICATION ENGINEERING" in department:
        department_code = "106"
        cgpa_department = "B.TECH ECE"
    elif "MECHANICAL ENGINEERING" in department:
        department_code = "102"
        cgpa_department = "BE.MECH"
    elif "INFORMATION TECHNOLOGY" in department:
        department_code = "105"
        cgpa_department = "B.TECH IT"
    elif "CIVIL ENGINEERING" in department:
        department_code = "101"
        cgpa_department = "BE.CIVIL"
    elif "COMPUTER SCIENCE AND ENGINEERING" in department:
        department_code = "104"
        cgpa_department = "B.TECH CSE"
    elif "ELECRICAL AND ELECTRONICS ENGINEERING" in department:
        department_code = "103"
        cgpa_department ="B.TECH EEE"

    # Get all students from placement portal database for the specific department and batch
    all_students = Student_cgpa.objects.using('rit_cgpatrack').filter(
        batch=project_batch,
        department= "B.TECH AD" , # Use the mapped department name
    )
    print(all_students, "all students")
    total_students = all_students.count()
    print(total_students, "total students")
    # Calculate submission percentage
    submission_percentage = round((total_projects_submitted / total_students) * 100) if total_students > 0 else 0
    
    # Get all students who have marks awarded
    total_marks_awarded = review_marks_master.objects.filter(
        department=department
    ).values('reg_no').distinct().count()

    # Calculate review completion percentage
    review_percentage = round((total_marks_awarded / total_projects_submitted) * 100) if total_projects_submitted > 0 else 0

    # Get students who haven't submitted projects (filtered by department and batch)
    submitted_student_regnos = list(projects_list.values_list('reg_no', flat=True))
    
    # Filter students who haven't submitted projects
    students_without_projects = Student_cgpa.objects.using('rit_cgpatrack').filter(
        batch=current_batch,
        department=cgpa_department  # Use the mapped department name
    ).exclude(
        reg_no__in=submitted_student_regnos
    )

    pending_submissions = max(0, total_students - total_projects_submitted)


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
    courses = Course.objects.using('rit_course_master').filter(department=course_department, semester=8)
    
    projects_list = Project.objects.filter(department=department)
    regulation = regulation_master.objects.using('rit_course_master').all()
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
    courses = Course.objects.using('rit_course_master').filter(department=course_department, semester=8)
    
    projects_list = Project.objects.filter(department=department)
    regulation = regulation_master.objects.using('rit_course_master').all()
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
    courses = Course.objects.using('rit_course_master').filter(department=course_department, semester=8)
    
    projects_list = Project.objects.filter(department=department)
    regulation = regulation_master.objects.using('rit_course_master').all()
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
        review3_comments = request.POST.get('review3_comments', '')  # Get comments from form

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
                'desegnation': designation,
                'review3_comments': review3_comments,  # Add comments to the model
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
    
    # Get all projects for the department
    projects = Project.objects.filter(department=department1)

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
                    internal_guide_name=faculty.Name,
                    hod_assigned_reviewer=True  # Set the reviewer as assigned
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

def update_guide(request):
    if request.method == "POST":
        project_id = request.POST.get("project_id")
        faculty_id = request.POST.get("faculty_id")
        
        if not project_id or not faculty_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Missing required parameters'
            })
            
        try:
            # Get the project and faculty
            project = Project.objects.get(id=project_id)
            faculty = User.objects.using('rit_e_approval').get(id=faculty_id)
            
            # Update the project with the new guide
            project.internal_guide_name = faculty.Name
            project.hod_assigned_reviewer = True  # Ensure this is marked as assigned
            project.save()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Successfully updated guide to {faculty.Name}'
            })
            
        except Project.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Project not found'
            })
        except User.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Faculty member not found'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
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
        reviewer_type = request.POST.get('reviewer_type')

        try:
            semester = int(semester_value) if semester_value not in [None, ''] else 0
        except ValueError:
            semester = 0
        
        course_code = request.POST.get('course_code')
        
        # Get marks for each criteria
        criteria_scores = [int(request.POST.get(f'criteria_{i}', 0)) for i in range(1, 11)]
        total = sum(criteria_scores)
        
        assign_record = assignreviewers.objects.filter(coursecode=course_code, department=department).first()
        batch, regulations, company_guide_name = ("", "", "")

        if assign_record:
            batch = assign_record.batch
            regulations = assign_record.regulation  
            company_guide_name = assign_record.company_name

        # Ensure marks are entered only once per faculty-reviewer-student combination
        if not review_marks_master.objects.filter(reg_no=reg_no, review_number=1, reviewer_type=reviewer_type, faculty_name=faculty_name).exists():
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
                total=total,
                **{f'criteria_{i+1}': criteria_scores[i] for i in range(10)}
            )
        
        return JsonResponse({'status': 'success'})

    # Handling GET request
    projects_list = Project.objects.filter(department=department)

    # Check if the faculty is a reviewer for Review 1
    assigned_projects = assignreviewers.objects.filter(
        department=department,
        review_type="Review 1"
    ).filter(
        Q(reviewer1=name) | Q(reviewer2=name) | Q(reviewer3=name)
    )

    is_reviewer = assigned_projects.exists()

    # Get students this faculty has already marked as guide
    students_marked_as_guide = review_marks_master.objects.filter(
        department=department,
        review_number=1,
        reviewer_type="Guide",
        faculty_name=name
    ).values_list('reg_no', flat=True)

    # Get students this faculty has already marked as reviewer
    students_marked_as_reviewer = review_marks_master.objects.filter(
        department=department,
        review_number=1,
        reviewer_type__startswith="Reviewer",
        faculty_name=name
    ).values_list('reg_no', flat=True)

    # Guide students who haven't been marked by this guide
    guide_students = Project.objects.filter(
        department=department,
        internal_guide_name=name
    ).exclude(reg_no__in=students_marked_as_guide)

    # If faculty is a reviewer, get students they are assigned to but haven't marked yet as reviewer
    reviewer_students = Project.objects.filter(
        department=department,
        batch__in=assigned_projects.values_list('batch', flat=True)
    ).exclude(reg_no__in=students_marked_as_reviewer) if is_reviewer else Project.objects.none()

    # Get review criteria for Review 1
    review_criteria = review_assasment_criteria_master.objects.filter(review_number=1).order_by('id')

    # Determine reviewer type for display
    reviewer_type = "Reviewer 1" if is_reviewer else "Guide"

    return render(request, 'faculty/review/review1_markentry.html', {
        'projects_list': projects_list,
        'is_reviewer': is_reviewer,
        'guide_students': guide_students,
        'reviewer_students': reviewer_students,
        'role': role,
        'department': department,
        'name': name,
        'review_criteria': review_criteria,
        'reviewer_type': reviewer_type
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
        reviewer_type = request.POST.get('reviewer_type')

        try:
            semester = int(semester_value) if semester_value not in [None, ''] else 0
        except ValueError:
            semester = 0
        
        course_code = request.POST.get('course_code')
        
        # Get marks for each criteria
        criteria_scores = [int(request.POST.get(f'criteria_{i}', 0)) for i in range(1, 11)]
        total = sum(criteria_scores)
        
        assign_record = assignreviewers.objects.filter(coursecode=course_code, department=department).first()
        batch, regulations, company_guide_name = ("", "", "")

        if assign_record:
            batch = assign_record.batch
            regulations = assign_record.regulation  
            company_guide_name = assign_record.company_name

        # Ensure marks are entered only once per faculty-reviewer-student combination
        if not review_marks_master.objects.filter(reg_no=reg_no, review_number=2, reviewer_type=reviewer_type, faculty_name=faculty_name).exists():
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
                total=total,
                **{f'criteria_{i+1}': criteria_scores[i] for i in range(10)}
            )
        
        return JsonResponse({'status': 'success'})

    # Handling GET request
    projects_list = Project.objects.filter(department=department)

    # Check if the faculty is a reviewer for Review 2
    assigned_projects = assignreviewers.objects.filter(
        department=department,
        review_type="Review 2"
    ).filter(
        Q(reviewer1=name) | Q(reviewer2=name) | Q(reviewer3=name)
    )

    is_reviewer = assigned_projects.exists()

    # Get students this faculty has already marked as guide
    students_marked_as_guide = review_marks_master.objects.filter(
        department=department,
        review_number=2,
        reviewer_type="Guide",
        faculty_name=name
    ).values_list('reg_no', flat=True)

    # Get students this faculty has already marked as reviewer
    students_marked_as_reviewer = review_marks_master.objects.filter(
        department=department,
        review_number=2,
        reviewer_type__startswith="Reviewer",
        faculty_name=name
    ).values_list('reg_no', flat=True)

    # Guide students who haven't been marked by this guide
    guide_students = Project.objects.filter(
        department=department,
        internal_guide_name=name
    ).exclude(reg_no__in=students_marked_as_guide)

    # If faculty is a reviewer, get students they are assigned to but haven't marked yet as reviewer
    reviewer_students = Project.objects.filter(
        department=department,
        batch__in=assigned_projects.values_list('batch', flat=True)
    ).exclude(reg_no__in=students_marked_as_reviewer) if is_reviewer else Project.objects.none()

    # Get review criteria for Review 2
    review_criteria = review_assasment_criteria_master.objects.filter(review_number=2).order_by('id')

    # Determine reviewer type for display
    reviewer_type = "Reviewer 1" if is_reviewer else "Guide"

    return render(request, 'faculty/review/review2_markentry.html', {
        'projects_list': projects_list,
        'is_reviewer': is_reviewer,
        'guide_students': guide_students,
        'reviewer_students': reviewer_students,
        'role': role,
        'department': department,
        'name': name,
        'review_criteria': review_criteria,
        'reviewer_type': reviewer_type
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
        reviewer_type = request.POST.get('reviewer_type')
        review3_comments = request.POST.get('review3_comments', '')  # Get comments from form

        try:
            semester = int(semester_value) if semester_value not in [None, ''] else 0
        except ValueError:
            semester = 0
        
        course_code = request.POST.get('course_code')
        
        # Get marks for each criteria
        criteria_scores = [int(request.POST.get(f'criteria_{i}', 0)) for i in range(1, 11)]
        total = sum(criteria_scores)
        
        assign_record = assignreviewers.objects.filter(coursecode=course_code, department=department).first()
        batch, regulations, company_guide_name = ("", "", "")

        if assign_record:
            batch = assign_record.batch
            regulations = assign_record.regulation  
            company_guide_name = assign_record.company_name

        # Ensure marks are entered only once per faculty-reviewer-student combination
        if not review_marks_master.objects.filter(reg_no=reg_no, review_number=3, reviewer_type=reviewer_type, faculty_name=faculty_name).exists():
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
                total=total,
                review3_comments=review3_comments,  # Add comments to the model
                **{f'criteria_{i+1}': criteria_scores[i] for i in range(10)}
            )
        
        return JsonResponse({'status': 'success'})

    # Handling GET request
    projects_list = Project.objects.filter(department=department)

    # Check if the faculty is a reviewer for Review 3
    assigned_projects = assignreviewers.objects.filter(
        department=department,
        review_type="Review 3"
    ).filter(
        Q(reviewer1=name) | Q(reviewer2=name) | Q(reviewer3=name)
    )

    is_reviewer = assigned_projects.exists()

    # Get students this faculty has already marked as guide
    students_marked_as_guide = review_marks_master.objects.filter(
        department=department,
        review_number=3,
        reviewer_type="Guide",
        faculty_name=name
    ).values_list('reg_no', flat=True)

    # Get students this faculty has already marked as reviewer
    students_marked_as_reviewer = review_marks_master.objects.filter(
        department=department,
        review_number=3,
        reviewer_type__startswith="Reviewer",
        faculty_name=name
    ).values_list('reg_no', flat=True)

    # Guide students who haven't been marked by this guide
    guide_students = Project.objects.filter(
        department=department,
        internal_guide_name=name
    ).exclude(reg_no__in=students_marked_as_guide)

    # If faculty is a reviewer, get students they are assigned to but haven't marked yet as reviewer
    reviewer_students = Project.objects.filter(
        department=department,
        batch__in=assigned_projects.values_list('batch', flat=True)
    ).exclude(reg_no__in=students_marked_as_reviewer) if is_reviewer else Project.objects.none()

    # Get review criteria for Review 3
    review_criteria = review_assasment_criteria_master.objects.filter(review_number=3).order_by('id')

    # Determine reviewer type for display
    reviewer_type = "Reviewer 1" if is_reviewer else "Guide"

    return render(request, 'faculty/review/review3_markentry.html', {
        'projects_list': projects_list,
        'is_reviewer': is_reviewer,
        'guide_students': guide_students,
        'reviewer_students': reviewer_students,
        'role': role,
        'department': department,
        'name': name,
        'review_criteria': review_criteria,
        'reviewer_type': reviewer_type
    })



def downlod_review_marks(request):
    role = request.session.get('role')
    department = request.session.get('department')
    name = request.session.get('name')
    return render(request, "faculty/review/downlod_review_marks.html",{
        'role': role,
        'department': department,
        'name': name
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



from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from .models import Project, assignreviewers, review_marks_master

from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from .models import Project, assignreviewers, review_marks_master

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
        reviewer_type = request.POST.get('reviewer_type')
        if not reviewer_type:
            reviewer_type = 'Guide'

        try:
            semester = int(semester_value) if semester_value not in [None, ''] else 0
        except ValueError:
            semester = 0
        
        course_code = request.POST.get('course_code')
        
        # Get marks for each criteria
        criteria_scores = [int(request.POST.get(f'criteria_{i}', 0)) for i in range(1, 11)]
        total = sum(criteria_scores)
        
        assign_record = assignreviewers.objects.filter(coursecode=course_code, department=department).first()
        batch, regulations, company_guide_name = ("", "", "")

        if assign_record:
            batch = assign_record.batch
            regulations = assign_record.regulation  
            company_guide_name = assign_record.company_name

        # Ensure marks are entered only once per faculty-reviewer-student combination
        if not review_marks_master.objects.filter(reg_no=reg_no, review_number=1, reviewer_type=reviewer_type, faculty_name=faculty_name).exists():
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
                total=total,
                **{f'criteria_{i+1}': criteria_scores[i] for i in range(10)}
            )
        
        return JsonResponse({'status': 'success'})

    # Handling GET request
    projects_list = Project.objects.filter(department=department)

    # Check if the faculty is a reviewer for Review 1 and determine which reviewer number
    assigned_projects = assignreviewers.objects.filter(
        department=department,
        review_type="Review 1"
    )
    
    # Determine which reviewer position the faculty holds
    reviewer_position = None
    if assigned_projects.filter(reviewer1=name).exists():
        reviewer_position = "Reviewer 1"
    elif assigned_projects.filter(reviewer2=name).exists():
        reviewer_position = "Reviewer 2"
    elif assigned_projects.filter(reviewer3=name).exists():
        reviewer_position = "Reviewer 3"
    
    is_reviewer = reviewer_position is not None

    # Get students this faculty has already marked as guide
    students_marked_as_guide = review_marks_master.objects.filter(
        department=department,
        review_number=1,
        reviewer_type="Guide",
        faculty_name=name
    ).values_list('reg_no', flat=True)

    # Get students this faculty has already marked as reviewer
    students_marked_as_reviewer = review_marks_master.objects.filter(
        department=department,
        review_number=1,
        reviewer_type__startswith="Reviewer",
        faculty_name=name
    ).values_list('reg_no', flat=True)

    # Guide students who haven't been marked by this guide
    guide_students = Project.objects.filter(
        department=department,
        internal_guide_name=name
    ).exclude(reg_no__in=students_marked_as_guide)

    # If faculty is a reviewer, get students they are assigned to but haven't marked yet as reviewer
    reviewer_students = Project.objects.filter(
        department=department,
        batch__in=assigned_projects.values_list('batch', flat=True)
    ).exclude(reg_no__in=students_marked_as_reviewer) if is_reviewer else Project.objects.none()

    # Get review criteria for Review 1
    review_criteria = review_assasment_criteria_master.objects.filter(review_number=1).order_by('id')

    # Use the determined reviewer position or default to "Guide"
    reviewer_type = reviewer_position if is_reviewer else "Guide"

    return render(request, 'faculty/review/faculty_review1_markentry.html', {
        'projects_list': projects_list,
        'is_reviewer': is_reviewer,
        'guide_students': guide_students,
        'reviewer_students': reviewer_students,
        'role': role,
        'department': department,
        'name': name,
        'review_criteria': review_criteria,
        'reviewer_type': reviewer_type
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
        reviewer_type = request.POST.get('reviewer_type')
        if not reviewer_type:
            reviewer_type = 'Guide'

        try:
            semester = int(semester_value) if semester_value not in [None, ''] else 0
        except ValueError:
            semester = 0
        
        course_code = request.POST.get('course_code')
        
        # Get marks for each criteria
        criteria_scores = [int(request.POST.get(f'criteria_{i}', 0)) for i in range(1, 11)]
        total = sum(criteria_scores)
        
        assign_record = assignreviewers.objects.filter(coursecode=course_code, department=department).first()
        batch, regulations, company_guide_name = ("", "", "")

        if assign_record:
            batch = assign_record.batch
            regulations = assign_record.regulation  
            company_guide_name = assign_record.company_name

        # Ensure marks are entered only once per faculty-reviewer-student combination
        if not review_marks_master.objects.filter(reg_no=reg_no, review_number=2, reviewer_type=reviewer_type, faculty_name=faculty_name).exists():
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
                total=total,
                **{f'criteria_{i+1}': criteria_scores[i] for i in range(10)}
            )
        
        return JsonResponse({'status': 'success'})

    # Handling GET request
    projects_list = Project.objects.filter(department=department)

    # Check if the faculty is a reviewer for Review 2 and determine which reviewer number
    assigned_projects = assignreviewers.objects.filter(
        department=department,
        review_type="Review 2"
    )
    
    # Determine which reviewer position the faculty holds
    reviewer_position = None
    if assigned_projects.filter(reviewer1=name).exists():
        reviewer_position = "Reviewer 1"
    elif assigned_projects.filter(reviewer2=name).exists():
        reviewer_position = "Reviewer 2"
    elif assigned_projects.filter(reviewer3=name).exists():
        reviewer_position = "Reviewer 3"
    
    is_reviewer = reviewer_position is not None

    # Get students this faculty has already marked as guide
    students_marked_as_guide = review_marks_master.objects.filter(
        department=department,
        review_number=2,
        reviewer_type="Guide",
        faculty_name=name
    ).values_list('reg_no', flat=True)

    # Get students this faculty has already marked as reviewer
    students_marked_as_reviewer = review_marks_master.objects.filter(
        department=department,
        review_number=2,
        reviewer_type__startswith="Reviewer",
        faculty_name=name
    ).values_list('reg_no', flat=True)

    # Guide students who haven't been marked by this guide
    guide_students = Project.objects.filter(
        department=department,
        internal_guide_name=name
    ).exclude(reg_no__in=students_marked_as_guide)

    # If faculty is a reviewer, get students they are assigned to but haven't marked yet as reviewer
    reviewer_students = Project.objects.filter(
        department=department,
        batch__in=assigned_projects.values_list('batch', flat=True)
    ).exclude(reg_no__in=students_marked_as_reviewer) if is_reviewer else Project.objects.none()

    # Get review criteria for Review 2
    review_criteria = review_assasment_criteria_master.objects.filter(review_number=2).order_by('id')

    # Use the determined reviewer position or default to "Guide"
    reviewer_type = reviewer_position if is_reviewer else "Guide"

    return render(request, 'faculty/review/faculty_review2_markentry.html', {
        'projects_list': projects_list,
        'is_reviewer': is_reviewer,
        'guide_students': guide_students,
        'reviewer_students': reviewer_students,
        'role': role,
        'department': department,
        'name': name,
        'review_criteria': review_criteria,
        'reviewer_type': reviewer_type
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
        reviewer_type = request.POST.get('reviewer_type')

        # If reviewer_type is not provided, default to 'Guide'
        if not reviewer_type:
            reviewer_type = 'Guide'

        try:
            semester = int(semester_value) if semester_value not in [None, ''] else 0
        except ValueError:
            semester = 0
        
        course_code = request.POST.get('course_code')
        
        # Get marks for each criteria
        criteria_scores = [int(request.POST.get(f'criteria_{i}', 0)) for i in range(1, 11)]
        total = sum(criteria_scores)
        
        assign_record = assignreviewers.objects.filter(coursecode=course_code, department=department).first()
        batch, regulations, company_guide_name = ("", "", "")

        if assign_record:
            batch = assign_record.batch
            regulations = assign_record.regulation  
            company_guide_name = assign_record.company_name

        # Ensure marks are entered only once per faculty-reviewer-student combination
        if not review_marks_master.objects.filter(reg_no=reg_no, review_number=3, reviewer_type=reviewer_type, faculty_name=faculty_name).exists():
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
                total=total,
                **{f'criteria_{i+1}': criteria_scores[i] for i in range(10)}
            )
        
        return JsonResponse({'status': 'success'})

    # Handling GET request
    projects_list = Project.objects.filter(department=department)

    # Check if the faculty is a reviewer for Review 3
    assigned_projects = assignreviewers.objects.filter(
        department=department,
        review_type="Review 3"
    ).filter(
        Q(reviewer1=name) | Q(reviewer2=name) | Q(reviewer3=name)
    )

    is_reviewer = assigned_projects.exists()

    # Get students this faculty has already marked as guide
    students_marked_as_guide = review_marks_master.objects.filter(
        department=department,
        review_number=3,
        reviewer_type="Guide",
        faculty_name=name
    ).values_list('reg_no', flat=True)

    # Get students this faculty has already marked as reviewer
    students_marked_as_reviewer = review_marks_master.objects.filter(
        department=department,
        review_number=3,
        reviewer_type__startswith="Reviewer",
        faculty_name=name
    ).values_list('reg_no', flat=True)

    # Guide students who haven't been marked by this guide
    guide_students = Project.objects.filter(
        department=department,
        internal_guide_name=name
    ).exclude(reg_no__in=students_marked_as_guide)

    # If faculty is a reviewer, get students they are assigned to but haven't marked yet as reviewer
    reviewer_students = Project.objects.filter(
        department=department,
        batch__in=assigned_projects.values_list('batch', flat=True)
    ).exclude(reg_no__in=students_marked_as_reviewer) if is_reviewer else Project.objects.none()

    # Get review criteria for Review 3
    review_criteria = review_assasment_criteria_master.objects.filter(review_number=3).order_by('id')

    # Determine reviewer type for display
    reviewer_type = "Reviewer 1" if is_reviewer else "Guide"

    return render(request, 'faculty/review/faculty_review3_markentry.html', {
        'projects_list': projects_list,
        'is_reviewer': is_reviewer,
        'guide_students': guide_students,
        'reviewer_students': reviewer_students,
        'role': role,
        'department': department,
        'name': name,
        'review_criteria': review_criteria,
        'reviewer_type': reviewer_type
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
    
    # Calculate achieved and total counts for each outcome type
    national_achieved = projects.filter(achieved="Yes", outcome="National Conference").count()
    national_total = projects.filter(outcome="National Conference").count()
    
    international_achieved = projects.filter(achieved="Yes", outcome="International Conference").count()
    international_total = projects.filter(outcome="International Conference").count()
    
    sci_achieved = projects.filter(achieved="Yes", outcome="SCI").count()
    sci_total = projects.filter(outcome="SCI").count()
    
    scie_achieved = projects.filter(achieved="Yes", outcome="SCIE").count()
    scie_total = projects.filter(outcome="SCIE").count()
    
    ugc_achieved = projects.filter(achieved="Yes", outcome="UGC").count()
    ugc_total = projects.filter(outcome="UGC").count()
    
    context = {
        'role': role,
        'name': name,
        'selected_department': selected_department,
        'available_departments': available_departments,
        'national_achieved': national_achieved,
        'national_total': national_total,
        'international_achieved': international_achieved,
        'international_total': international_total,
        'sci_achieved': sci_achieved,
        'sci_total': sci_total,
        'scie_achieved': scie_achieved,
        'scie_total': scie_total,
        'ugc_achieved': ugc_achieved,
        'ugc_total': ugc_total,
    }
    
    return render(request, 'faculty/criteria_analysis.html', context)

def export_to_excel(request):
    department = request.session.get('department')
    review_number = request.GET.get('review', None)
    
    # Get all projects for the department
    projects = Project.objects.filter(department=department)
    
    # Create lists to store the data
    data = []
    
    for project in projects:
        # Get all review marks for this project
        review_marks = review_marks_master.objects.filter(
            reg_no=project.reg_no,
            department=department
        )
        
        if review_number != '4':  # For specific review
            review_marks = review_marks.filter(review_number=review_number)
        
        if review_marks.exists():
            # Initialize marks for each review
            guide_totals = []
            reviewer1_totals = []
            reviewer2_totals = []
            reviewer3_totals = []
            
            # Process each review mark
            for mark in review_marks:
                # Calculate total marks for this review
                criteria_marks = [
                    mark.criteria_1 or 0,
                    mark.criteria_2 or 0,
                    mark.criteria_3 or 0,
                    mark.criteria_4 or 0,
                    mark.criteria_5 or 0,
                    mark.criteria_6 or 0,
                    mark.criteria_7 or 0,
                    mark.criteria_8 or 0,
                    mark.criteria_9 or 0,
                    mark.criteria_10 or 0
                ]
                total_marks = sum(criteria_marks)
                
                if mark.reviewer_type == 'Guide':
                    guide_totals.append(total_marks)
                elif mark.reviewer_type == 'Reviewer 1':
                    reviewer1_totals.append(total_marks)
                elif mark.reviewer_type == 'Reviewer 2':
                    reviewer2_totals.append(total_marks)
                elif mark.reviewer_type == 'Reviewer 3':
                    reviewer3_totals.append(total_marks)
            
            # Get the highest marks for each reviewer type
            guide_total = max(guide_totals) if guide_totals else None
            reviewer1_total = max(reviewer1_totals) if reviewer1_totals else None
            reviewer2_total = max(reviewer2_totals) if reviewer2_totals else None
            reviewer3_total = max(reviewer3_totals) if reviewer3_totals else None
            
            # Calculate average from non-null values
            valid_marks = [m for m in [guide_total, reviewer1_total, reviewer2_total, reviewer3_total] if m is not None]
            average = sum(valid_marks) / len(valid_marks) if valid_marks else None
            
            # Create row with all data
            row = {
                'Student Name': project.student_name,
                'Registration Number': project.reg_no,
                'Guide Total': f"{guide_total:.2f}" if guide_total is not None else '-',
                'Reviewer 1 Total': f"{reviewer1_total:.2f}" if reviewer1_total is not None else '-',
                'Reviewer 2 Total': f"{reviewer2_total:.2f}" if reviewer2_total is not None else '-',
                'Reviewer 3 Total': f"{reviewer3_total:.2f}" if reviewer3_total is not None else '-',
                'Average': f"{average:.2f}" if average is not None else '-'
            }
            data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    excel_file = BytesIO()
    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
        sheet_name = 'All Reviews Marks' if review_number == '4' else f'Review {review_number} Marks'
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        
        # Add formatting
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#00407b',  # Matching the table header color
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        # Format cells
        cell_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        # Format the header row
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 20)  # Set column width
        
        # Format data cells
        for row_num in range(len(df)):
            for col_num in range(len(df.columns)):
                worksheet.write(row_num + 1, col_num, df.iloc[row_num, col_num], cell_format)
    
    # Set up the response
    excel_file.seek(0)
    response = HttpResponse(
        excel_file.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    
    filename = 'all_reviews_marks' if review_number == '4' else f'review_{review_number}_marks'
    response['Content-Disposition'] = f'attachment; filename={filename}_{department}_{datetime.now().strftime("%Y%m%d")}.xlsx'
    
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

def student_forgot_password(request):
    if request.method == 'POST':
        if 'registration_number' in request.POST:
            # First step: Verify registration number
            registration_number = request.POST.get('registration_number')
            try:
                student = Student.objects.using('placement_portal').get(student_regno=registration_number)
                # Store registration number in session for next step
                request.session['reset_reg_no'] = registration_number
                return render(request, 'student/forgot_password.html', {'new_password_form': True})
            except Student.DoesNotExist:
                messages.error(request, 'Invalid registration number. Please try again.')
                return render(request, 'student/forgot_password.html', {'new_password_form': False})
        
        elif 'new_password' in request.POST:
            # Second step: Set new password
            registration_number = request.session.get('reset_reg_no')
            if not registration_number:
                messages.error(request, 'Session expired. Please try again.')
                return redirect('student_forgot_password')
            
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if new_password != confirm_password:
                messages.error(request, 'Passwords do not match. Please try again.')
                return render(request, 'student/forgot_password.html', {'new_password_form': True})
            
            try:
                student = Student.objects.using('placement_portal').get(student_regno=registration_number)
                student.student_password = encrypt_password(new_password)  # Update password with encryption
                student.save()
                messages.success(request, 'Password has been reset successfully. Please login with your new password.')
                # Clear the session
                if 'reset_reg_no' in request.session:
                    del request.session['reset_reg_no']
                return redirect('student_login')
            except Student.DoesNotExist:
                messages.error(request, 'Student not found. Please try again.')
                return redirect('student_forgot_password')
    
    # GET request - show initial form
    return render(request, 'student/forgot_password.html', {'new_password_form': False})

def get_review_preview(request, review_number):
    try:
        department = request.session.get('department')
        
        # Get all review marks for this department
        if review_number == 4:
            # For all reviews, get data from all review numbers
            review_marks = review_marks_master.objects.filter(department=department)
        else:
            # For specific review, filter by review number
            review_marks = review_marks_master.objects.filter(
                department=department,
                review_number=review_number
            )
        
        # Group marks by student registration number
        student_data = {}
        
        for mark in review_marks:
            if mark.reg_no not in student_data:
                student_data[mark.reg_no] = {
                    'student_name': mark.student_name,
                    'reg_no': mark.reg_no,
                    'guide_total': None,
                    'guide_name': None,
                    'reviewer1_total': None,
                    'reviewer1_name': None,
                    'reviewer2_total': None,
                    'reviewer2_name': None,
                    'reviewer3_total': None,
                    'reviewer3_name': None,
                    'average': None
                }
            
            # Calculate total marks for this review
            criteria_marks = [
                mark.criteria_1 or 0,
                mark.criteria_2 or 0,
                mark.criteria_3 or 0,
                mark.criteria_4 or 0,
                mark.criteria_5 or 0,
                mark.criteria_6 or 0,
                mark.criteria_7 or 0,
                mark.criteria_8 or 0,
                mark.criteria_9 or 0,
                mark.criteria_10 or 0
            ]
            total_marks = sum(criteria_marks)
            
            # For all reviews (review_number == 4), update with highest marks
            if review_number == 4:
                if mark.reviewer_type == 'Guide':
                    if student_data[mark.reg_no]['guide_total'] is None or total_marks > student_data[mark.reg_no]['guide_total']:
                        student_data[mark.reg_no]['guide_total'] = total_marks
                        student_data[mark.reg_no]['guide_name'] = mark.faculty_name
                elif mark.reviewer_type == 'Reviewer 1':
                    if student_data[mark.reg_no]['reviewer1_total'] is None or total_marks > student_data[mark.reg_no]['reviewer1_total']:
                        student_data[mark.reg_no]['reviewer1_total'] = total_marks
                        student_data[mark.reg_no]['reviewer1_name'] = mark.faculty_name
                elif mark.reviewer_type == 'Reviewer 2':
                    if student_data[mark.reg_no]['reviewer2_total'] is None or total_marks > student_data[mark.reg_no]['reviewer2_total']:
                        student_data[mark.reg_no]['reviewer2_total'] = total_marks
                        student_data[mark.reg_no]['reviewer2_name'] = mark.faculty_name
                elif mark.reviewer_type == 'Reviewer 3':
                    if student_data[mark.reg_no]['reviewer3_total'] is None or total_marks > student_data[mark.reg_no]['reviewer3_total']:
                        student_data[mark.reg_no]['reviewer3_total'] = total_marks
                        student_data[mark.reg_no]['reviewer3_name'] = mark.faculty_name
            else:
                # For specific review, just update the marks
                if mark.reviewer_type == 'Guide':
                    student_data[mark.reg_no]['guide_total'] = total_marks
                    student_data[mark.reg_no]['guide_name'] = mark.faculty_name
                elif mark.reviewer_type == 'Reviewer 1':
                    student_data[mark.reg_no]['reviewer1_total'] = total_marks
                    student_data[mark.reg_no]['reviewer1_name'] = mark.faculty_name
                elif mark.reviewer_type == 'Reviewer 2':
                    student_data[mark.reg_no]['reviewer2_total'] = total_marks
                    student_data[mark.reg_no]['reviewer2_name'] = mark.faculty_name
                elif mark.reviewer_type == 'Reviewer 3':
                    student_data[mark.reg_no]['reviewer3_total'] = total_marks
                    student_data[mark.reg_no]['reviewer3_name'] = mark.faculty_name
        
        # Convert dictionary to list and calculate averages
        preview_data = []
        for student in student_data.values():
            # Calculate average from non-None values
            totals = [
                student['guide_total'],
                student['reviewer1_total'],
                student['reviewer2_total'],
                student['reviewer3_total']
            ]
            valid_totals = [t for t in totals if t is not None]
            average = sum(valid_totals) / len(valid_totals) if valid_totals else None
            
            student['average'] = round(average, 2) if average is not None else None
            preview_data.append(student)
        
        return JsonResponse(preview_data, safe=False)
        
    except Exception as e:
        print(f"Error in get_review_preview: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
def criteria_entry(request):
    role = request.session.get('role')
    department = request.session.get('department')
    name = request.session.get('name')

    return render(request,  "faculty/criteria_entry.html", {
        'role': role,
        'department': department,
        'name': name
    })

def get_criteria(request, review_number):
    try:
        criteria_list = review_assasment_criteria_master.objects.filter(review_number=review_number)
        criteria_data = [{'review_criteria': criteria.review_criteria} for criteria in criteria_list]
        return JsonResponse(criteria_data, safe=False)
    except Exception as e:
        print(f"Error fetching criteria: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def update_criteria(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            review_number = data.get('review_number')
            criteria_index = data.get('criteria_index')
            new_value = data.get('new_value')

            # Get all criteria for this review number
            criteria_list = review_assasment_criteria_master.objects.filter(review_number=review_number)
            
            if criteria_index < len(criteria_list):
                # Update the specific criteria
                criteria = criteria_list[criteria_index]
                criteria.review_criteria = new_value
                criteria.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Criteria not found'}, status=404)
                
        except Exception as e:
            print(f"Error updating criteria: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
def analysis_student_mark(request):
    role = request.session.get('role')
    department = request.session.get('department')
    name = request.session.get('name')

    if role == 'HOD':
        print(f"[DEBUG] Fetching students for department: {department}")
        # Get all students from the department
        students = Project.objects.filter(department=department).values(
            'student_name', 'reg_no', 'batch'
        ).distinct()
        print(f"[DEBUG] Found {students.count()} students")

        # Add semester information and rename reg_no to register_number
        for student in students:
            student['semester'] = '8'  # Default to 8th semester for final year students
            # Keep both reg_no and register_number
            student['register_number'] = student['reg_no']
            print(f"[DEBUG] Student: {student['student_name']}, reg_no: {student['reg_no']}")

        context = {
            'role': role,
            'department': department,
            'name': name,
            'students': students
        }
        
        return render(request, 'faculty/review/analysis_student_mark.html', context)
    else:
        # Check if faculty is a guide
        guide_students = Project.objects.filter(
            department=department,
            internal_guide_name=name
        ).values(
            'student_name', 'reg_no', 'batch'
        ).distinct()

        # Add semester information and rename reg_no to register_number
        for student in guide_students:
            student['semester'] = '8'  # Default to 8th semester for final year students
            student['register_number'] = student['reg_no']

        context = {
            'role': role,
            'department': department,
            'name': name,
            'students': guide_students,
            'is_guide': True
        }
        
        return render(request, 'faculty/review/analysis_student_mark.html', context)

def student_review_analysis(request, register_number, review_number):
    role = request.session.get('role')
    department = request.session.get('department')
    name = request.session.get('name')

    # Check if user is HOD or a guide for this student
    is_guide = False
    if role != 'HOD':
        # Check if faculty is a guide for this student
        is_guide = Project.objects.filter(
            reg_no=register_number,
            department=department,
            internal_guide_name=name
        ).exists()
        
        if not is_guide:
            return redirect('home_page')

    try:
        print(f"[DEBUG] Looking for student with reg_no={register_number}")
        # Get student details
        student = Project.objects.get(reg_no=register_number)
        print(f"[DEBUG] Found student: {student.student_name}")
        
        # Convert review_number to integer if it's a string
        review_number = int(review_number)
        
        # Get review marks
        review_marks_query = review_marks_master.objects.filter(reg_no=register_number)
        print(f"[DEBUG] Found {review_marks_query.count()} review marks")
        
        if review_number != 4:
            review_marks_query = review_marks_query.filter(review_number=review_number)
            print(f"[DEBUG] After filtering for review {review_number}, found {review_marks_query.count()} review marks")
        
        review_marks = review_marks_query.order_by('review_number', 'reviewer_type')
        
        # Get criteria list based on review number
        if review_number == 4:
            # For "All Reviews", get criteria from all reviews
            criteria_list = []
            for rev_num in range(1, 4):
                criteria = review_assasment_criteria_master.objects.filter(review_number=rev_num).order_by('id')
                criteria_list.append({
                    'review_number': rev_num,
                    'criteria': list(criteria)
                })
        else:
            # For specific reviews, get criteria for that review
            criteria = review_assasment_criteria_master.objects.filter(review_number=review_number).order_by('id')
            criteria_list = [{
                'review_number': review_number,
                'criteria': list(criteria)
            }]
        
        print(f"[DEBUG] Found criteria for reviews: {[c['review_number'] for c in criteria_list]}")
        
        # Initialize data structures
        review_data = []
        
        # Process each review's data
        for review_info in criteria_list:
            rev_num = review_info['review_number']
            rev_criteria = review_info['criteria']
            
            print(f"[DEBUG] Processing review {rev_num}")
            
            # Get marks for this review
            rev_marks = review_marks_query.filter(review_number=rev_num)
            guide_marks = rev_marks.filter(reviewer_type='Guide').first()
            reviewer1_marks = rev_marks.filter(reviewer_type='Reviewer 1').first()
            reviewer2_marks = rev_marks.filter(reviewer_type='Reviewer 2').first()
            reviewer3_marks = rev_marks.filter(reviewer_type='Reviewer 3').first()
            
            # Process criteria marks
            criteria_marks = []
            review_total = {
                'guide_total': 0,
                'reviewer1_total': 0,
                'reviewer2_total': 0,
                'reviewer3_total': 0
            }
            
            for idx, criteria in enumerate(rev_criteria, 1):
                print(f"[DEBUG] Processing criteria {idx} for review {rev_num}")
                
                criteria_data = {
                    'name': criteria.review_criteria,
                    'guide_mark': None,
                    'reviewer1_mark': None,
                    'reviewer2_mark': None,
                    'reviewer3_mark': None
                }
                
                # Get guide marks
                if guide_marks:
                    mark_value = getattr(guide_marks, f'criteria_{idx}', None)
                    if mark_value is not None:
                        criteria_data['guide_mark'] = float(mark_value)
                        review_total['guide_total'] += float(mark_value)
                
                # Get reviewer 1 marks
                if reviewer1_marks:
                    mark_value = getattr(reviewer1_marks, f'criteria_{idx}', None)
                    if mark_value is not None:
                        criteria_data['reviewer1_mark'] = float(mark_value)
                        review_total['reviewer1_total'] += float(mark_value)
                
                # Get reviewer 2 marks
                if reviewer2_marks:
                    mark_value = getattr(reviewer2_marks, f'criteria_{idx}', None)
                    if mark_value is not None:
                        criteria_data['reviewer2_mark'] = float(mark_value)
                        review_total['reviewer2_total'] += float(mark_value)
                
                # Get reviewer 3 marks
                if reviewer3_marks:
                    mark_value = getattr(reviewer3_marks, f'criteria_{idx}', None)
                    if mark_value is not None:
                        criteria_data['reviewer3_mark'] = float(mark_value)
                        review_total['reviewer3_total'] += float(mark_value)
                
                # Calculate average
                valid_marks = [v for v in [
                    criteria_data['guide_mark'],
                    criteria_data['reviewer1_mark'],
                    criteria_data['reviewer2_mark'],
                    criteria_data['reviewer3_mark']
                ] if v is not None]
                criteria_data['average'] = sum(valid_marks) / len(valid_marks) if valid_marks else None
                
                criteria_marks.append(criteria_data)
            
            # Calculate review averages
            valid_totals = [v for v in review_total.values() if v > 0]
            review_total['average'] = sum(valid_totals) / len(valid_totals) if valid_totals else None
            
            # Format totals
            for key in review_total:
                if isinstance(review_total[key], (int, float)) and review_total[key] > 0:
                    review_total[key] = f"{review_total[key]:.2f}"
                else:
                    review_total[key] = "-"
            
            review_data.append({
                'review_number': rev_num,
                'criteria_marks': criteria_marks,
                'totals': review_total,
                'guide_name': guide_marks.faculty_name if guide_marks else None,
                'reviewer1_name': reviewer1_marks.faculty_name if reviewer1_marks else None,
                'reviewer2_name': reviewer2_marks.faculty_name if reviewer2_marks else None,
                'reviewer3_name': reviewer3_marks.faculty_name if reviewer3_marks else None
            })
        
        # Calculate grand totals for all reviews
        grand_totals = {
            'guide_total': 0,
            'reviewer1_total': 0,
            'reviewer2_total': 0,
            'reviewer3_total': 0,
            'average_total': 0
        }
        
        valid_review_count = 0
        for review in review_data:
            guide_total = float(review['totals']['guide_total']) if review['totals']['guide_total'] != '-' else 0
            reviewer1_total = float(review['totals']['reviewer1_total']) if review['totals']['reviewer1_total'] != '-' else 0
            reviewer2_total = float(review['totals']['reviewer2_total']) if review['totals']['reviewer2_total'] != '-' else 0
            reviewer3_total = float(review['totals']['reviewer3_total']) if review['totals']['reviewer3_total'] != '-' else 0
            
            if any([guide_total > 0, reviewer1_total > 0, reviewer2_total > 0, reviewer3_total > 0]):
                valid_review_count += 1
                grand_totals['guide_total'] += guide_total
                grand_totals['reviewer1_total'] += reviewer1_total
                grand_totals['reviewer2_total'] += reviewer2_total
                grand_totals['reviewer3_total'] += reviewer3_total
                
                valid_marks = [m for m in [guide_total, reviewer1_total, reviewer2_total, reviewer3_total] if m > 0]
                if valid_marks:
                    grand_totals['average_total'] += sum(valid_marks) / len(valid_marks)
        
        # Format grand totals
        if valid_review_count > 0:
            for key in grand_totals:
                if grand_totals[key] > 0:
                    grand_totals[key] = f"{grand_totals[key] / valid_review_count:.2f}"
                else:
                    grand_totals[key] = "-"
        else:
            grand_totals = {key: "-" for key in grand_totals}
        
        context = {
            'student': {
                'student_name': student.student_name,
                'register_number': register_number
            },
            'review_number': str(review_number),
            'review_data': review_data,
            'grand_totals': grand_totals,
            'is_guide': is_guide
        }
        
        print(f"[DEBUG] Rendering template with context: {context}")
        return render(request, 'faculty/review/student_review_analysis.html', context)
        
    except Project.DoesNotExist:
        print(f"[DEBUG] Student not found with reg_no={register_number}")
        messages.error(request, 'Student not found')
        return redirect('analysis_student_mark')
    except Exception as e:
        print(f"[DEBUG] Error in student_review_analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        messages.error(request, f'Error: {str(e)}')
        return redirect('analysis_student_mark')

@login_required
def get_student_analytics(request, register_number):
    try:
        print(f"[DEBUG] Fetching analytics for student: {register_number}")
        review_number = request.GET.get('review_number')
        print(f"[DEBUG] Review number requested: {review_number}")
        
        if not review_number:
            return JsonResponse({'error': 'Review number is required'}, status=400)
        
        # Get student details from Project model
        try:
            student = Project.objects.get(reg_no=register_number)
            print(f"[DEBUG] Found student: {student.student_name}")
        except Project.DoesNotExist:
            print(f"[DEBUG] Student not found: {register_number}")
            return JsonResponse({'error': 'Student not found'}, status=404)
        
        # Initialize response data
        response_data = {
            'student_name': student.student_name,
            'register_number': register_number,
            'guide_marks': {},
            'review1_marks': {},
            'review2_marks': {},
            'review3_marks': {},
            'guide_name': None,
            'reviewer1_name': None,
            'reviewer2_name': None,
            'reviewer3_name': None,
            'detailed_marks': []
        }
        
        # Get all review marks for this student
        review_marks_query = review_marks_master.objects.filter(reg_no=register_number)
        print(f"[DEBUG] Initial query count: {review_marks_query.count()}")
        
        if review_number != '4':
            # Filter for specific review
            review_marks_query = review_marks_query.filter(review_number=int(review_number))
            print(f"[DEBUG] Fetching marks for review {review_number}")
        else:
            print("[DEBUG] Fetching marks for all reviews")
        
        review_marks = review_marks_query.order_by('review_number', 'reviewer_type')
        print(f"[DEBUG] Found {review_marks.count()} review marks")
        
        # Process each review mark
        for mark in review_marks:
            print(f"[DEBUG] Processing mark: Review {mark.review_number}, {mark.reviewer_type}")
            
            # Create marks dictionary
            marks_dict = {}
            for i in range(1, 11):
                criteria_value = getattr(mark, f'criteria_{i}')
                if criteria_value is not None:
                    marks_dict[f'criteria_{i}'] = float(criteria_value)
            
            # Calculate total
            valid_marks = [v for v in marks_dict.values() if v is not None]
            total = sum(valid_marks) if valid_marks else None
            print(f"[DEBUG] Calculated total for {mark.reviewer_type}: {total}")
            
            # Update response data based on reviewer type and review number
            if mark.reviewer_type == 'Guide':
                response_data['guide_marks'].update(marks_dict)
                response_data['guide_name'] = mark.faculty_name
                print(f"[DEBUG] Updated guide marks, guide name: {mark.faculty_name}")
            else:
                review_key = f'review{mark.review_number}_marks'
                reviewer_key = f'reviewer{mark.review_number}_name'
                response_data[review_key].update(marks_dict)
                response_data[reviewer_key] = mark.faculty_name
                print(f"[DEBUG] Updated {review_key}, reviewer name: {mark.faculty_name}")
            
            # Add to detailed marks
            detailed_mark = {
                'review_number': mark.review_number,
                'guide_total': total if mark.reviewer_type == 'Guide' else None,
                'reviewer_total': total if mark.reviewer_type.startswith('Reviewer') else None
            }
            
            # Check if we already have a record for this review number
            existing_mark = next(
                (m for m in response_data['detailed_marks'] if m['review_number'] == mark.review_number),
                None
            )
            
            if existing_mark:
                if mark.reviewer_type == 'Guide':
                    existing_mark['guide_total'] = total
                else:
                    existing_mark['reviewer_total'] = total
                
                # Calculate average if both totals are available
                if existing_mark['guide_total'] is not None and existing_mark['reviewer_total'] is not None:
                    existing_mark['average_total'] = (existing_mark['guide_total'] + existing_mark['reviewer_total']) / 2
                print(f"[DEBUG] Updated existing mark for review {mark.review_number}")
            else:
                response_data['detailed_marks'].append(detailed_mark)
                print(f"[DEBUG] Added new detailed mark for review {mark.review_number}")
        
        print("[DEBUG] Response data prepared successfully")
        print("[DEBUG] Response data:", response_data)
        return JsonResponse(response_data)
    
    except Project.DoesNotExist:
        print(f"[DEBUG] Student not found: {register_number}")
        return JsonResponse({'error': 'Student not found'}, status=404)
    except Exception as e:
        print(f"[DEBUG] Error in get_student_analytics: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

def get_student_analytics_all(request):
    if request.session.get('role') == 'HOD':
        try:
            department = request.session.get('department')
            
            # Get all students in the department
            students = Project.objects.filter(department=department)
            
            all_students_data = []
            
            for student in students:
                # Get review marks for each student
                for review_number in [1, 2, 3]:
                    review_marks = review_marks_master.objects.filter(
                        reg_no=student.reg_no,
                        review_number=review_number,
                        department=department
                    ).order_by('reviewer_type')
                    
                    if review_marks.exists():
                        # Get criteria for this review
                        criteria_list = review_assasment_criteria_master.objects.filter(
                            review_number=review_number
                        ).order_by('id')
                        
                        # Process marks
                        guide_marks = review_marks.filter(reviewer_type='Guide').first()
                        reviewer_marks = review_marks.filter(reviewer_type='Reviewer').order_by('id')
                        
                        marks_data = {
                            'student_name': student.student_name,
                            'register_number': student.reg_no,
                            'batch': student.batch,
                            'semester': student.semester,
                            'review_number': review_number,
                            'guide_marks': {},
                            'reviewer1_marks': {},
                            'reviewer2_marks': {},
                            'reviewer3_marks': {}
                        }
                        
                        # Process guide marks
                        if guide_marks:
                            for i, criteria in enumerate(criteria_list, 1):
                                mark_value = getattr(guide_marks, f'criteria_{i}', None)
                                if mark_value is not None:
                                    marks_data['guide_marks'][f'criteria_{i}'] = float(mark_value)
                        
                        # Process reviewer marks
                        for idx, reviewer_mark in enumerate(reviewer_marks[:3], 1):
                            for i, criteria in enumerate(criteria_list, 1):
                                mark_value = getattr(reviewer_mark, f'criteria_{i}', None)
                                if mark_value is not None:
                                    marks_data[f'reviewer{idx}_marks'][f'criteria_{i}'] = float(mark_value)
                        
                        all_students_data.append(marks_data)
            
            return JsonResponse(all_students_data, safe=False)
            
        except Exception as e:
            print(f"Error fetching all students analytics: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Unauthorized'}, status=403)

def get_review_marks(request, review_number):
    if request.session.get('role') == 'HOD':
        try:
            department = request.session.get('department')
            
            # Get all marks for this review in the department
            review_marks = review_marks_master.objects.filter(
                review_number=review_number,
                department=department
            ).order_by('register_number')
            
            # Group marks by student
            students_data = {}
            for mark in review_marks:
                if mark.reg_no not in students_data:
                    students_data[mark.reg_no] = {
                        'student_name': mark.student_name,
                        'register_number': mark.reg_no,
                        'batch': mark.batch,
                        'semester': mark.semester,
                        'guide_marks': None,
                        'reviewer1_marks': None,
                        'reviewer2_marks': None,
                        'reviewer3_marks': None
                    }
                
                # Create marks dictionary
                marks_dict = {
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
                
                # Assign marks to appropriate reviewer type
                if mark.reviewer_type == 'Guide':
                    students_data[mark.reg_no]['guide_marks'] = marks_dict
                elif mark.reviewer_type == 'Reviewer':
                    # Find first empty reviewer slot
                    for i in range(1, 4):
                        reviewer_key = f'reviewer{i}_marks'
                        if students_data[mark.reg_no][reviewer_key] is None:
                            students_data[mark.reg_no][reviewer_key] = marks_dict
                            break
            
            return JsonResponse(list(students_data.values()), safe=False)
            
        except Exception as e:
            print(f"Error fetching review {review_number} marks: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Unauthorized'}, status=403)



from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from traceback import format_exc

def get_review_marks_master(request, review_number):
    try:
        department = request.GET.get('department', None)
        print(f"Fetching marks for review {review_number}, department: {department}")
        
        # Filter marks by review number and department
        marks_query = review_marks_master.objects.filter(review_number=review_number)
        if department:
            marks_query = marks_query.filter(department=department)
        
        mark_count = marks_query.count()
        print(f"Found {mark_count} records")
        
        if mark_count == 0:
            return JsonResponse([], safe=False)
        
        marks_data = {}
        
        for mark in marks_query:
            try:
                # Convert criteria marks to float and handle None values
                criteria_marks = {}
                for i in range(1, 11):
                    value = getattr(mark, f'criteria_{i}', None)
                    criteria_marks[f'criteria_{i}'] = float(value) if value is not None else None
                
                if mark.reg_no not in marks_data:
                    marks_data[mark.reg_no] = {
                        'register_number': mark.reg_no,
                        'student_name': mark.student_name,
                        'guide_marks': None,
                        'reviewer1_marks': None,
                        'reviewer2_marks': None,
                        'reviewer3_marks': None
                    }
                
                if mark.reviewer_type == 'Guide':
                    marks_data[mark.reg_no]['guide_marks'] = criteria_marks
                else:
                    for i in range(1, 4):
                        key = f'reviewer{i}_marks'
                        if marks_data[mark.reg_no][key] is None:
                            marks_data[mark.reg_no][key] = criteria_marks
                            break
            
            except Exception as e:
                print(f"Error processing mark {mark.reg_no}: {e}\n{format_exc()}")
                continue
        
        # Convert the dictionary to a list of values
        result = list(marks_data.values())
        print(f"Successfully processed {len(result)} marks records")
        
        # Ensure all values are JSON serializable
        serializable_result = []
        for item in result:
            serializable_item = {
                'register_number': str(item['register_number']),
                'student_name': str(item['student_name']),
                'guide_marks': item['guide_marks'],
                'reviewer1_marks': item['reviewer1_marks'],
                'reviewer2_marks': item['reviewer2_marks'],
                'reviewer3_marks': item['reviewer3_marks']
            }
            serializable_result.append(serializable_item)
        
        return JsonResponse(serializable_result, safe=False)
    
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Requested data not found'}, status=404)
    except Exception as e:
        print(f"Error in get_review_marks_master: {e}\n{format_exc()}")
        return JsonResponse({'error': str(e)}, status=500)
