from django.urls import path
from . import views
from projects.views import admin_portal
urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('faculty_login/', views.faculty_login, name='faculty_login'),
    path('faculty_dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('student_login/', views.student_login, name='student_login'),
    path('student_entry/', views.student_entry, name='student_entry'),
    path('view_status/', views.view_status, name='view_status'),
    path('view_marks/', views.view_marks, name='view_marks'),
    path('hod_dashbord/', views.hod_dashbord, name='hod_dashbord'),
    path('admin/admin_portal',admin_portal,name="admin_portal"),
    # path('allocate_commity/', views.allocate_commity, name='allocate_commity'),
    path('review1/', views.review1, name='review1'),
    path('review2/', views.review2, name='review2'),
    path('review3/', views.review3, name='review3'),
    path('guide_alocation/', views.guide_alocation, name='guide_alocation'),
    path('review_mark_allotment/', views.review_mark_allotment, name='review_mark_allotment'),
    path('review1_markentry/', views.review1_markentry, name='review1_markentry'),
    path('review2_markentry/', views.review2_markentry, name='review2_markentry'),
    path('review3_markentry/', views.review3_markentry, name='review3_markentry'),
    path('faculty_review1_markentry/', views.faculty_review1_markentry, name='faculty_review1_markentry'),
    path('faculty_review2_markentry/', views.faculty_review2_markentry, name='faculty_review2_markentry'),
    path('faculty_review3_markentry/', views.faculty_review3_markentry, name='faculty_review3_markentry'),
    # path("assign_reviewers/", views.assign_reviewers, name="assign_reviewers"),

]
