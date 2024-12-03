from django.shortcuts import render

def login_page(request):
    return render(request, 'login.html')
def student_login(request):
    return render(request, 'student_login.html')
def faculty_login(request):
    return render(request, 'faculty_login.html')

