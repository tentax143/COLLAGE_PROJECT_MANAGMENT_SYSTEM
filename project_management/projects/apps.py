from django.apps import AppConfig
from django.contrib.auth import get_user_model
import os

class ProjectsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'projects'

    def ready(self):
        if os.environ.get('RUN_MAIN') == 'true':  # Prevent duplicate execution during development
            from django.contrib.auth.models import User
            User = get_user_model()
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser('admin', 'admin@example.com', 'mk4997320')
                print("Superuser 'admin' created successfully.")
