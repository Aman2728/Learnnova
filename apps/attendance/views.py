from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from apps.users.models import User
from .models import Attendance
from utils.jwt import decode_access_token
from utils.decorators import admin_required
import json
from datetime import date



# -----------------------------
# TEACHER MARK ATTENDANCE
# -----------------------------

@csrf_exempt
def mark_attendance(request):

    if request.method != "POST":
        return JsonResponse({"success": False, "message": "POST request required"})

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return JsonResponse({"success": False, "message": "Token required"}, status=401)

    try:
        token = auth_header.split(" ")[1]
        payload = decode_access_token(token)

        # check if token is valid
        if payload is None:
            return JsonResponse({
                "success": False,
                "message": "Invalid or expired token"
            }, status=401)

        teacher = User.objects.get(id=payload["user_id"])

        body = json.loads(request.body) if request.body else {}
        status = body.get("status", "present")

        today = date.today()

        # prevent duplicate attendance
        if Attendance.objects.filter(teacher=teacher, date=today).exists():
            return JsonResponse({
                "success": False,
                "message": "Attendance already marked today"
            })

        Attendance.objects.create(
            teacher=teacher,
            status=status
        )

        return JsonResponse({
            "success": True,
            "message": f"Attendance marked {status}"
        })

    except User.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Teacher not found"
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": str(e)
        })


# -----------------------------
# ADMIN VIEW ALL TEACHER ATTENDANCE
# -----------------------------
@admin_required
def teacher_attendance_list(request):

    attendance = Attendance.objects.select_related("teacher").all().order_by("-date")

    data = []

    for a in attendance:
        data.append({
            "teacher_id": a.teacher.id,
            "teacher_name":a.teacher.username,
            "date": a.date,
            "time": a.time, 
            "status": a.status
            
        })

    return JsonResponse({
        "success": True,
        "attendance": data
    })





@csrf_exempt
def my_attendance(request):

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return JsonResponse({
            "success": False,
            "message": "Token required"
        }, status=401)

    try:
        token = auth_header.split(" ")[1]
        payload = decode_access_token(token)

        if payload is None:
            return JsonResponse({
                "success": False,
                "message": "Invalid token"
            }, status=401)

        teacher = User.objects.get(id=payload["user_id"])

        attendance = Attendance.objects.filter(
            teacher=teacher
        ).order_by("date")

        data = []

        for a in attendance:
            data.append({
                "date": a.date,
                "status": a.status
            })

        return JsonResponse({
            "success": True,
            "attendance": data
        })

    except User.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Teacher not found"
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": str(e)
        })




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import date
import json

from utils.decorators import student_required
from apps.users.models import User
from .models import StudentAttendance
from django.utils.timezone import now


import json
from datetime import date
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from utils.decorators import student_required
from .models import StudentAttendance


@csrf_exempt
@student_required
def mark_student_attendance(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "POST required"
        }, status=405)

    student = request.user
    today = date.today()

    # get data from frontend
    data = json.loads(request.body)
    status = data.get("status")

    if status not in ["present", "absent"]:
        return JsonResponse({
            "success": False,
            "message": "Invalid status"
        })

    # prevent duplicate attendance
    already = StudentAttendance.objects.filter(
        student=student,
        date=today
    ).first()

    if already:
        return JsonResponse({
            "success": False,
            "message": f"You already marked attendance at {already.time.strftime('%I:%M %p')}"
        })

    # create attendance
    attendance = StudentAttendance.objects.create(
        student=student,
        status=status
    )

    return JsonResponse({
        "success": True,
        "status": attendance.status,
        "time": attendance.time.strftime("%I:%M %p"),
        "date": str(attendance.date)
    })


@admin_required
def student_attendance_list(request):

    records = StudentAttendance.objects.select_related("student").all().order_by("-date","-time")

    data = []

    for r in records:

        data.append({
            "student_id": r.student.id,
            "student_name": r.student.username,
            "date": r.date,
            "time": r.time,
            "status": r.status
        })

    return JsonResponse({
        "success":True,
        "attendance":data
    })

from utils.decorators import admin_required

@admin_required
def student_attendance_list(request):

    records = StudentAttendance.objects.select_related("student").all().order_by("-date","-time")

    data = []

    for r in records:

        data.append({
            "student_id": r.student.id,
            "student_name": r.student.username,
            "date": str(r.date),
            "time": r.time.strftime("%H:%M"),
            "status": r.status
        })

    return JsonResponse({
        "success":True,
        "attendance":data
    })


@student_required
def my_student_attendance(request):

    student = request.user

    records = StudentAttendance.objects.filter(
        student=student
    ).order_by("date")

    data = []

    for r in records:
        data.append({
            "date": str(r.date),
            "status": r.status,
            "time": r.time.strftime("%I:%M %p")
        })

    return JsonResponse({
        "success": True,
        "attendance": data
    })