🎓 College Project Management System

A web-based application designed to streamline the management of college projects. This system facilitates efficient tracking, submission, and evaluation of student projects, enhancing collaboration between students and faculty.

🚀 Features
User Authentication: Secure login for students and faculty members.

Project Submission: Students can submit project details and documents.

Project Evaluation: Faculty can review and grade submitted projects.

Dashboard: Overview of project statuses and deadlines.

Notifications: Alerts for upcoming deadlines and feedback.

🛠️ Technologies Used
Frontend: HTML, CSS

Backend: Python

Database: [xampp,sqlite]

Version Control: Git
📂 Repository Structure
├── db.sqlite3
├── manage.py
├── media
│   └── outcome_certificates
│       └── 2021-2025
├── projects
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_projectsreviewmarksmaster.py
│   │   ├── 0003_alter_projectsreviewmarksmaster_options.py
│   │   ├── 0004_review_assasment_criteria_master_department_and_more.py
│   │   ├── 0005_reviewcomments.py
│   │   ├── 0006_alter_projectsreviewmarksmaster_table.py
│   │   ├── __init__.py
│   │   └── __pycache__
│   │       ├── 0001_initial.cpython-310.pyc
│   │       ├── 0002_projectsreviewmarksmaster.cpython-310.pyc
│   │       ├── 0003_alter_projectsreviewmarksmaster_options.cpython-310.pyc
│   │       ├── 0004_review_assasment_criteria_master_department_and_more.cpython-310.pyc
│   │       ├── 0005_reviewcomments.cpython-310.pyc
│   │       ├── 0006_alter_projectsreviewmarksmaster_table.cpython-310.pyc
│   │       └── __init__.cpython-310.pyc
│   ├── models.py
│   ├── static
│   │   ├── css
│   │   │   ├── auth.css
│   │   │   ├── style.css
│   │   │   ├── style1.css
│   │   │   ├── style2.css
│   │   │   └── style3.css
│   │   ├── images
│   │   │   ├── back.png
│   │   │   ├── background.jpg
│   │   │   ├── image.png
│   │   │   ├── rit.jpg
│   │   │   └── rit.png
│   │   └── pdf
│   │       ├── project_managment_manual.pdf
│   │       └── project_managment_manual_old.pdf
│   ├── templates
│   │   ├── base.html
│   │   ├── faculty
│   │   │   ├── base.html
│   │   │   ├── criteria_analysis.html
│   │   │   ├── criteria_entry.html
│   │   │   ├── faculty_dashboard.html
│   │   │   ├── faculty_login.html
│   │   │   ├── filter.html
│   │   │   ├── guide_alocation.html
│   │   │   ├── hod_dashbord.html
│   │   │   ├── principal_dashboard.html
│   │   │   ├── review
│   │   │   │   ├── analysis_student_mark.html
│   │   │   │   ├── downlod_review_marks.html
│   │   │   │   ├── faculty_review1_markentry.html
│   │   │   │   ├── faculty_review2_markentry.html
│   │   │   │   ├── faculty_review3_markentry.html
│   │   │   │   ├── final_outcome_entry.html
│   │   │   │   ├── mark_entry_form.html
│   │   │   │   ├── review1.html
│   │   │   │   ├── review1_markentry.html
│   │   │   │   ├── review2.html
│   │   │   │   ├── review2_markentry.html
│   │   │   │   ├── review3.html
│   │   │   │   ├── review3_markentry.html
│   │   │   │   └── student_review_analysis.html
│   │   │   ├── review2_markentry.html
│   │   │   └── review_mark_allotment.html
│   │   ├── hod
│   │   │   └── project_outcome_analysis.html
│   │   ├── home.html
│   │   └── student
│   │       ├── forgot_password.html
│   │       ├── login.html
│   │       ├── student_entry.html
│   │       ├── student_login.html
│   │       ├── success.html
│   │       ├── view_marks.html
│   │       └── view_status.html
│   ├── templatetags
│   │   └── __pycache__
│   │       ├── custom_filters.cpython-310.pyc
│   │       └── __init__.cpython-310.pyc
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── __init__.py
│   └── __pycache__
│       ├── admin.cpython-310.pyc
│       ├── admin.cpython-312.pyc
│       ├── apps.cpython-310.pyc
│       ├── apps.cpython-312.pyc
│       ├── models.cpython-310.pyc
│       ├── models.cpython-312.pyc
│       ├── urls.cpython-310.pyc
│       ├── urls.cpython-312.pyc
│       ├── views.cpython-310.pyc
│       ├── views.cpython-312.pyc
│       ├── __init__.cpython-310.pyc
│       └── __init__.cpython-312.pyc
└── project_management
    ├── asgi.py
    ├── media
    │   └── outcome_certificates
    │       └── 2021-2025
    │           └── ARTIFICIAL INTELLIGENCE AND DATA SCIENCE
    │               └── 953621243002
    │                   └── outcome_certificate_20250325_172546.pdf
    ├── settings.py
    ├── urls.py
    ├── wsgi.py
    ├── __init__.py
    └── __pycache__
        ├── settings.cpython-310.pyc
        ├── settings.cpython-312.pyc
        ├── urls.cpython-310.pyc
        ├── urls.cpython-312.pyc
        ├── wsgi.cpython-310.pyc
        ├── wsgi.cpython-312.pyc
        ├── __init__.cpython-310.pyc
        └── __init__.cpython-312.pyc

📝 Getting Started
Clone the repository:
  git clone https://github.com/tentax143/COLLAGE_PROJECT_MANAGMENT_SYSTEM.git
Navigate to the project directory:
  cd COLLAGE_PROJECT_MANAGMENT_SYSTEM
Install dependencies: 
  pip install -r requirements.txt
Run the application:
  python manage.py runserver
🤝 Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.
