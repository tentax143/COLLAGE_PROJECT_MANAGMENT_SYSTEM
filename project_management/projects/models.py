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
    reg_no = models.CharField(max_length=20, null=True, blank=True) 
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

# from django.db import models
# from django.contrib.auth.models import User  # Assuming faculty are users

# class AssignedReviewers(models.Model):
#     student_id = models.IntegerField()  # Assuming you are assigning reviewers to students
#     reviewer1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviewer1")
#     reviewer2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviewer2")
#     reviewer3 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviewer3")
#     assigned_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Reviewers for Student {self.student_id}"

class assignreviewers(models.Model):
    
    reviewer1=models.CharField(max_length=200, null=True,blank=True)
    reviewer2=models.CharField(max_length=200, null=True,blank=True)
    reviewer3=models.CharField(max_length=200, null=True,blank=True)
    assignedat=models.DateField(auto_now_add=True)
    regulation=models.CharField(max_length=200, null=True,blank=True)
    coursecode=models.CharField(max_length=200, null=True,blank=True)
    coursename=models.CharField(max_length=200, null=True,blank=True)
    batch=models.CharField(max_length=200, null=True,blank=True)
    sem=models.IntegerField()

class regulation_master(models.Model):
    regulation_year = models.IntegerField()
    regulation_name = models.CharField(max_length=100)
    class Meta:
        db_table = 'equipment_regulation_master'
        managed = False



