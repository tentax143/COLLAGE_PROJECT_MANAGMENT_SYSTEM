# Generated by Django 5.1.6 on 2025-03-07 06:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_project'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AssignedReviewers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_id', models.IntegerField()),
                ('assigned_at', models.DateTimeField(auto_now_add=True)),
                ('reviewer1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviewer1', to=settings.AUTH_USER_MODEL)),
                ('reviewer2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviewer2', to=settings.AUTH_USER_MODEL)),
                ('reviewer3', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviewer3', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
