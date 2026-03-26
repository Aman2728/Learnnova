from django.shortcuts import render


# Create your views here.


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Course
from utils.decorators import teacher_or_admin_required
from apps.users.models import User
import json



@csrf_exempt
@teacher_or_admin_required
def create_course(request):
    if request.method == "POST":

        if request.user.role != "admin":
            return JsonResponse({"success": False, "message": "Only admin can create course"}, status=403)

        try:
            data = json.loads(request.body)

            course = Course.objects.create(
                title=data.get("title"),
                description=data.get("description"),
                price=data.get("price"),
                duration_in_days=data.get("duration"),
                total_slots=data.get("total_slots"),
                remaining_slots=data.get("total_slots"),
                created_by=request.user
            )

            return JsonResponse({"success": True, "message": "Course created successfully"})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)

from decimal import Decimal

from decimal import Decimal

@csrf_exempt
@teacher_or_admin_required
def update_course(request, course_id):
    if request.method == "PUT":
        try:
            if request.user.role == "admin":
                course = Course.objects.get(id=course_id)
            else:
                course = Course.objects.get(id=course_id, teacher=request.user)

            data = json.loads(request.body)
            print("DATA:", data)  # 👈 DEBUG

            if data.get("title") is not None:
                course.title = data.get("title")

            if data.get("description") is not None:
                course.description = data.get("description")

            if data.get("price") is not None:
                course.price = Decimal(data.get("price"))

            if data.get("duration_in_days") is not None:
                course.duration_in_days = data.get("duration_in_days")

            if data.get("total_slots") is not None:
                course.total_slots = int(data.get("total_slots"))
                assigned_students = course.students.count()
                course.remaining_slots = course.total_slots - assigned_students

            if data.get("status") is not None:
                course.status = data.get("status")

            course.save()

            return JsonResponse({
                "success": True,
                "message": "Course updated successfully"
            })

        except Exception as e:
            print("ERROR:", e)
            return JsonResponse({
                "success": False,
                "message": str(e)
            }, status=400)

    return JsonResponse({"message": "Invalid request method"}, status=405)

@csrf_exempt
@teacher_or_admin_required
def delete_course(request, course_id):
    if request.method == "DELETE":
        try:
            # Admin → delete any course
            if request.user.role == "admin":
                course = Course.objects.get(id=course_id)
            else:
                # Teacher → delete only their own course
                course = Course.objects.get(id=course_id, teacher=request.user)

            course.delete()

            return JsonResponse({
                "success": True,
                "message": "Course deleted successfully"
            })

        except Course.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": "Course not found or access denied"
            }, status=404)

    return JsonResponse({"message": "Invalid request method"}, status=405)

    
from django.utils import timezone

@csrf_exempt
@teacher_or_admin_required
def assign_teacher(request, course_id):
    if request.method == "PUT":

        if request.user.role != "admin":
            return JsonResponse({"success": False, "message": "Only admin can assign teacher"}, status=403)

        try:
            data = json.loads(request.body)

            teacher_id = data.get("teacher_id")
            teacher = User.objects.get(id=teacher_id, role="teacher")

            course = Course.objects.get(id=course_id)

            course.teacher = teacher
            course.teacher_assigned_at = timezone.now()
            course.save()

            return JsonResponse({"success": True, "message": "Teacher assigned successfully"})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)

@csrf_exempt
@teacher_or_admin_required
def assign_student(request, course_id):
    if request.method == "PUT":
        try:
            data = json.loads(request.body)

            student_id = data.get("student_id")
            student = User.objects.get(id=student_id, role="student")

            course = Course.objects.get(id=course_id)

            if course.remaining_slots <= 0:
                return JsonResponse({"success": False, "message": "No slots available"})

            course.students.add(student)
            course.remaining_slots -= 1
            course.save()

            return JsonResponse({"success": True, "message": "Student assigned successfully"})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)

@teacher_or_admin_required
def list_all_courses(request):

    if request.user.role != "admin":
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=403)

    courses = Course.objects.all()

    data = []

    for course in courses:
        data.append({
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "price": str(course.price),
            "duration_in_days": course.duration_in_days,
            "total_slots": course.total_slots,
            "remaining_slots": course.remaining_slots,
            "teacher": course.teacher.username if course.teacher else None,
            "students_count": course.students.count(),
            "status": course.status,
            "created_by": course.created_by.username if course.created_by else None,
            "teacher_assigned_at": course.teacher_assigned_at,
            "created_at": course.created_at
        })

    return JsonResponse({
        "success": True,
        "courses": data
    })

@teacher_or_admin_required
def teacher_courses(request):

    if request.user.role != "teacher":
        return JsonResponse({"success": False}, status=403)

    courses = Course.objects.filter(teacher=request.user)

    data = []

    for course in courses:

        students_list = []

        for student in course.students.all():
            students_list.append({
                "id": student.id,
                "name": student.username
            })

        data.append({
            "id": course.id,
            "title": course.title,
            "students": course.students.count(),
            "students_list": students_list
        })

    return JsonResponse({
        "success": True,
        "courses": data
    })


def student_courses(request):

    if request.user.role != "student":
        return JsonResponse({"success": False}, status=403)

    courses = request.user.enrolled_courses.all()

    data = []
    for course in courses:
       data.append({
    "id": course.id,
    "title": course.title,
    "description": course.description,
    "teacher": course.teacher.username if course.teacher else None
})

    return JsonResponse({"success": True, "courses": data})    



from django.http import JsonResponse
from apps.users.models import User
from utils.jwt import decode_access_token


def get_all_teachers(request):

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return JsonResponse({"success": False, "message": "Token required"}, status=401)

    try:
        token = auth_header.split(" ")[1]
        decode_access_token(token)

        teachers = User.objects.filter(role="teacher")

        teacher_list = []

        for teacher in teachers:
            teacher_list.append({
                "id": teacher.id,
                "name": teacher.username
            })

        return JsonResponse({
            "success": True,
            "teachers": teacher_list
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": str(e)
        })        



def get_all_students(request):

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return JsonResponse({"success": False}, status=401)

    token = auth_header.split(" ")[1]
    decode_access_token(token)

    students = User.objects.filter(role="student")

    data = []

    for s in students:
        data.append({
            "id": s.id,
            "name": s.username
        })

    return JsonResponse({
        "success": True,
        "students": data
    })







from django.http import JsonResponse
from utils.jwt import decode_access_token
from apps.users.models import User


def get_profile(request):

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return JsonResponse({"success": False, "message": "Token required"}, status=401)

    try:
        token = auth_header.split(" ")[1]
        payload = decode_access_token(token)

        user = User.objects.get(id=payload["user_id"])

        return JsonResponse({
            "success": True,
            "name": user.username,
            "role": user.role
        })

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})












from django.http import JsonResponse
from utils.jwt import decode_access_token
from apps.users.models import User
from .models import Course

def teacher_students(request):

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return JsonResponse({"success": False, "message": "Token required"}, status=401)

    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)

    teacher = User.objects.get(id=payload["user_id"])

    # get courses of this teacher
    courses = Course.objects.filter(teacher=teacher)

    students = []

    for course in courses:
        for student in course.students.all():

            students.append({
                "id": student.id,
                "name": student.username,
               "class": getattr(student, "student_class", "N/A"),
                "attendance": "90%",
                "grade": "80%"
            })

    return JsonResponse({
        "success": True,
        "students": students
    })