from django.urls import path
from . import views

urlpatterns = [

    path("create/", views.create_assignment),

    path("teacher/", views.teacher_assignments),

    path("student/", views.student_assignments),

    path("submit/", views.submit_assignment),

    path("submissions/", views.assignment_submissions),
]