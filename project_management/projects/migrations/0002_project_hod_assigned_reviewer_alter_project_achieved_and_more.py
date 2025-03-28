# Generated by Django 5.0.6 on 2025-03-27 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='hod_assigned_reviewer',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='achieved',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='batch',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='project',
            name='company_guide_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='company_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='course_code',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='course_title',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='department',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='project',
            name='domain',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='project',
            name='entry_status',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='project',
            name='internal_guide_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='location',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='outcome',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='outcome_certificate',
            field=models.FileField(blank=True, null=True, upload_to='outcome_certificates/'),
        ),
        migrations.AlterField(
            model_name='project',
            name='project_outcome_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='project_type',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='project',
            name='student_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='title',
            field=models.CharField(max_length=200),
        ),
    ]
