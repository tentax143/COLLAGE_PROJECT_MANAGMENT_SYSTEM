from django.urls import path
from . import views
from projects.views import admin_portal
from .views import get_review_preview
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
    path('final_outcome_entry/', views.final_outcome_entry, name='final_outcome_entry'),
    path('filter/', views.filter, name='filter'),
    path('principal_dashboard/', views.principal_dashboard, name='principal_dashboard'),
    path('criteria_analysis/', views.criteria_analysis, name='criteria_analysis'),
    path('export_to_excel/', views.export_to_excel, name='export_to_excel'),
    path('export_to_excel/', views.export_to_excel, name='export_to_excel'),
    path('download_certificate/<str:reg_no>/', views.download_certificate, name='download_certificate'),
    path('student/forgot-password/', views.student_forgot_password, name='student_forgot_password'),
    path('downlod_review_marks/', views.downlod_review_marks, name='downlod_review_marks'),
    path('get_review_preview/<int:review_number>/', views.get_review_preview, name='get_review_preview'),
    path('criteria_entry/', views.criteria_entry, name='criteria_entry'),
    path('get-criteria/<int:review_number>/', views.get_criteria, name='get_criteria'),
    path('get_review<int:review_number>_marks/', views.get_review_marks, name='get_review_marks'),
    path('update-criteria/', views.update_criteria, name='update_criteria'),
    path('analysis_student_mark/', views.analysis_student_mark, name='analysis_student_mark'),
    path('get_student_analytics/all/', views.get_student_analytics_all, name='get_student_analytics_all'),
    path('get_student_analytics/<str:register_number>/', views.get_student_analytics, name='get_student_analytics'),
    path('get-review-marks-master/<int:review_number>/', views.get_review_marks_master, name='get_review_marks_master'),
    path('get_review_preview/<int:review_number>/', get_review_preview, name='get_review_preview'),
]



