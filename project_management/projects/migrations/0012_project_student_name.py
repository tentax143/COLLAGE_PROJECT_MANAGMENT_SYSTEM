# Generated by Django 5.1.6 on 2025-03-07 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0011_student_cgpa_assignreviewers_batch_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='student_name',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
