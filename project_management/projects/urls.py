from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login_page'),
    path('faculty_login/', views.faculty_login, name='faculty_login'),
    path('student_login/', views.student_login, name='student_login'),
]
