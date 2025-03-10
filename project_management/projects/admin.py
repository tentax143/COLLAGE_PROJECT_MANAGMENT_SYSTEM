from django.contrib import admin

# Register your models here.

import django.apps

# Register your models here.
class project_managment(admin.AdminSite):
    site_header='ADMIN'
admin_site=project_managment(name='RIT Admin')
models=django.apps.apps.get_models()
for model in models:
    try:
        admin_site.register(model)
    except:
        print("model not found")
