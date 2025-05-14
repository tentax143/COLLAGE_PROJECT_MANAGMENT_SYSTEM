# 🎓 Project Management & Review System

A Django-based web application to manage and streamline student project reviews, assessment criteria, faculty interactions, and certificate generation for academic institutions.

---

## 📂 Folder Structure

```
├── db.sqlite3
├── manage.py
├── media/
│   └── outcome_certificates/
│       └── 2021-2025/
├── projects/
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── static/
│   │   ├── css/
│   │   ├── images/
│   │   └── pdf/
│   ├── templates/
│   │   ├── base.html
│   │   ├── faculty/
│   │   ├── hod/
│   │   ├── student/
│   │   └── home.html
│   ├── templatetags/
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   └── __init__.py
├── project_management/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── __init__.py
```

---

## 💡 Features

- 🔐 Role-based logins for Students, Faculty, HOD, and Principal
- 📥 Student project entry and review tracking
- 🧾 Faculty review entry for multiple stages (Review 1, 2, 3)
- 📊 Criteria-based evaluation and analysis dashboard
- 📤 Final outcome certificate generation
- 🧑‍🏫 HOD and Principal-level analytics and filtering
- 📎 Static files: CSS, images, PDFs
- 📄 Review comments and mark allocations
- 🖼️ Template-driven HTML for various roles

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd <repo-folder>
```

### 2. Set Up Virtual Environment (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> If `requirements.txt` is not available, install Django manually:
```bash
pip install django
```

### 4. Apply Migrations

```bash
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

---

## 📁 Static and Media Files

- Static files are located in `projects/static/`
- Uploaded media (certificates) are stored in `media/outcome_certificates/`
- To enable media serving in development, add this to your `urls.py`:

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 🧠 Roles and Dashboards

| Role       | Features |
|------------|----------|
| Student    | Login, project entry, view marks/status |
| Faculty    | Login, mark entry, review dashboards, final outcome |
| HOD        | View reports, outcome analysis |
| Principal  | Overall analysis dashboard |

---

## 📌 Notes

- This app is designed for multi-year project tracking.
- Ensure your `settings.py` is configured for media and static file handling.
- Email/password recovery not yet implemented — password reset via admin panel.

---

## 📜 License

MIT License – Feel free to use and modify.

---

## 🙏 Acknowledgements

Developed with ❤️ by Manish for academic use. Inspired by real-world academic processes and aimed to reduce manual project tracking.
