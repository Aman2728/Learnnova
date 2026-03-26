from django.urls import path
from .views import get_all_teachers
from .views import get_all_students
from .views import teacher_students
from .views import get_profile
from .views import (
    create_course,
    assign_teacher,
    assign_student,
    list_all_courses,
    teacher_courses,
    student_courses,
    update_course, 
    delete_course
)

urlpatterns = [
    path("course/create/", create_course),
    path("course/<int:course_id>/update/", update_course),
    path("course/<int:course_id>/delete/", delete_course),
    path("course/<int:course_id>/assign-teacher/", assign_teacher),
    path("course/<int:course_id>/assign-student/", assign_student),

    path("courses/all/", list_all_courses),
    path("courses/teacher/", teacher_courses),
    path("courses/student/", student_courses),
    path("teachers/all/", get_all_teachers),
    path("students/all/", get_all_students),
    path("profile/", get_profile),
    path("teacher/students/", teacher_students),

]