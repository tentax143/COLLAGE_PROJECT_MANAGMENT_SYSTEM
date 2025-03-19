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
    student_name=models.CharField(max_length=300, null=True,blank=True)
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
    semester = models.IntegerField(null=True,blank=True)
    course_code = models.CharField(max_length=10,null=True,blank=True)
    course_title = models.CharField(max_length=255,null=True,blank=True)



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
    review_type=models.CharField(max_length=100,null=True,blank=True)
    reviewer1=models.CharField(max_length=200, null=True,blank=True)
    reviewer2=models.CharField(max_length=200, null=True,blank=True)
    reviewer3=models.CharField(max_length=200, null=True,blank=True)
    assignedat=models.DateField(auto_now_add=True)
    regulation=models.CharField(max_length=200, null=True,blank=True)
    coursecode=models.CharField(max_length=200, null=True,blank=True)
    coursename=models.CharField(max_length=200, null=True,blank=True)
    batch=models.CharField(max_length=200, null=True,blank=True)
    sem=models.IntegerField()
    department=models.CharField(max_length=200, null=True,blank=True)
    expname=models.CharField(max_length=200, null=True,blank=True)
    company_name=models.CharField(max_length=200, null=True,blank=True)
    desegnation=models.CharField(max_length=200, null=True,blank=True)

class regulation_master(models.Model):
    regulation_year = models.IntegerField()
    regulation_name = models.CharField(max_length=100)
    class Meta:
        db_table = 'equipment_regulation_master'
        managed = False

# class review1(models.Model):


from django.db import models  # type: ignore


class Student_cgpa(models.Model):
    reg_no = models.CharField(max_length=20, primary_key=True)
    batch = models.CharField(max_length=100)
    student_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    # section = models.CharField(
    #     max_length=10, blank=True, null=True
    # )  # New field for section
    # gender = models.CharField(
    #     max_length=10,
    #     choices=[("Male", "Male"), ("Female", "Female")],
    #     blank=True,
    #     null=True,
    # )  # New field for gender
    cgpa = models.FloatField()
    sslc = models.FloatField()
    hsc = models.CharField(max_length=20, blank=True, null=True)
    diploma = models.CharField(max_length=20, blank=True, null=True)
    bag_of_log = models.IntegerField()
    history_of_arrear = models.IntegerField()
    admission_type = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)

    # Semester fields as CharField to store grades or GPAs
    semester1 = models.CharField(max_length=20, blank=True, null=True)
    semester2 = models.CharField(max_length=20, blank=True, null=True)
    semester3 = models.CharField(max_length=20, blank=True, null=True)
    semester4 = models.CharField(max_length=20, blank=True, null=True)
    semester5 = models.CharField(max_length=20, blank=True, null=True)
    semester6 = models.CharField(max_length=20, blank=True, null=True)
    semester7 = models.CharField(max_length=20, blank=True, null=True)
    semester8 = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = "application_student"
        managed = False  # Since the table already exists in the database

class SubjectType(models.Model):
    type_name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "subject_type_table"  # Custom table name
        managed= False
    def _str_(self):
        return self.type_name





class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "category_table"  # Custom table name
        managed= False
    def _str_(self):
        return self.category_name

class Course(models.Model):

    batch = models.CharField(max_length=50)
    regulations = models.CharField(max_length=20)
    # degree = models.CharField(max_length=10)
    department = models.CharField(max_length=50)
    semester = models.IntegerField()
    course_code = models.CharField(max_length=10)
    course_title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subject_type = models.ForeignKey(SubjectType, on_delete=models.CASCADE)
    lecturer = models.IntegerField()
    tutorial = models.IntegerField()
    practical = models.IntegerField()
    total_contact_periods = models.IntegerField()
    credits = models.IntegerField()

    class Meta:
        db_table = "course"
        managed= False

    def _str_(self):
        return f"{self.course_code} - {self.course_title}"
class review_marks_master(models.Model):
    faculty_name=models.CharField(max_length=100)
    faculty_role=models.CharField(max_length=100)
    reviewer_type=models.CharField(max_length=100)
    student_name= models.CharField(max_length=100)
    reg_no=models.CharField(max_length=20)
    batch = models.CharField(max_length=50)
    review_number=models.IntegerField()
    regulations = models.CharField(max_length=20)
    department = models.CharField(max_length=50)
    semester = models.IntegerField()
    course_code = models.CharField(max_length=10)
    company_guide_name = models.CharField(max_length=255, blank=True, null=True)
    internal_guide_name = models.CharField(max_length=255, blank=True, null=True)
    criteria_1=models.IntegerField()
    criteria_2=models.IntegerField()
    criteria_3=models.IntegerField()
    criteria_4=models.IntegerField()
    criteria_5=models.IntegerField()
    criteria_6=models.IntegerField()
    criteria_7=models.IntegerField()
    criteria_8=models.IntegerField()
    criteria_9=models.IntegerField()
    criteria_10=models.IntegerField()
    total=models.IntegerField()


class internal_review_mark(models.Model):
    student_name= models.CharField(max_length=100)
    reg_no=models.IntegerField()
    department = models.CharField(max_length=50)
    semester = models.IntegerField()
    course_code = models.CharField(max_length=10, unique=True)
    review_1=models.IntegerField()
    review_2=models.IntegerField()
    review_3=models.IntegerField()
    total=models.IntegerField()


class departments(models.Model):
    dept_code=models.CharField(max_length=200,primary_key=True)
    department=models.CharField(max_length=500)
    department_description=models.CharField(max_length=100)
    degree_code=models.IntegerField()
    class meta:
        db='rit_e_approval'
        db_table='application_departments'
        manage=False




