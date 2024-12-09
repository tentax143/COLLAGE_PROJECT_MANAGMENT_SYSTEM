from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('faculty_login/', views.faculty_login, name='faculty_login'),
    path('faculty_dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('student_login/', views.student_login, name='student_login'),
    path('student_entry/', views.student_entry, name='student_entry'),
]
