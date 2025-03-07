# Generated by Django 5.1.6 on 2025-03-07 07:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_delete_assignedreviewers'),
    ]

    operations = [
        migrations.CreateModel(
            name='assignreviewers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reg_no', models.IntegerField()),
                ('reviewer1', models.CharField(blank=True, max_length=200, null=True)),
                ('reviewer2', models.CharField(blank=True, max_length=200, null=True)),
                ('reviewer3', models.CharField(blank=True, max_length=200, null=True)),
                ('assignedat', models.DateField(auto_now_add=True)),
            ],
        ),
    ]
