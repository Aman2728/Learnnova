from django.urls import path
from . import views

urlpatterns = [

    path("mark/", views.mark_attendance),

    path("teachers/", views.teacher_attendance_list),
    path("my/", views.my_attendance),
    path("students/mark/",views.mark_student_attendance),
    path("students/",views.student_attendance_list),
    path("students/my/", views.my_student_attendance),

]