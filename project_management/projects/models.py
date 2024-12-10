from django.db import models

# Create your models here.
class Student(models.Model):
    student_regno = models.CharField(max_length=255, primary_key=True)
    student_dob = models.DateField(null=True, blank=True)
    student_password = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'core_student'
        managed = False
class User(models.Model):
    Name = models.CharField(max_length=100)
    user_name = models.CharField(max_length=100)
    staff_id = models.CharField(max_length=100)
    Department = models.CharField(max_length=100)
    Department_code=models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    default_role=models.CharField(max_length=200,null=True,blank=True)
    Password = models.CharField(max_length=100)
    confirm_Password = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.Name}-({self.role}-{self.staff_id})"
    class Meta:
        db_table = 'application_user'
        managed = False
class faculty_master(models.Model):
    faculty_id=models.IntegerField()
    faculty_name=models.CharField(max_length=200,null=True,blank=True)
    department=models.CharField(max_length=300,null=True,blank=True)
class Project(models.Model):
    department=models.CharField(max_length=300)
    batch=models.CharField(max_length=300)
    entry_status=models.CharField(max_length=300)
    title = models.CharField(max_length=255)
    domain = models.CharField(max_length=255)
    project_type = models.CharField(max_length=50, choices=[('internal', 'Internal'), ('external', 'External')])
    company_name = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    company_guide_name = models.CharField(max_length=255, blank=True, null=True)
    duration = models.CharField(max_length=50, blank=True, null=True)
    internal_guide_name = models.CharField(max_length=255, blank=True, null=True)