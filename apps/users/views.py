from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os
import datetime
import re
import random
import time
from .models import User
from django.views.decorators.csrf import csrf_exempt
from apps.users.models import OTP
import json
import re
import random
import time
from django.contrib.auth.hashers import make_password
from utils.jwt import generate_access_token
from django.contrib.auth.hashers import check_password
from utils.otp_sender import send_otp_email
from utils.admin_required import admin_required





def success_response(message, data=None, status=200):
    return JsonResponse({
        "success": True,
        "message": message,
        "data": data
    }, status=status)


def error_response(message, errors=None, status=400):
    return JsonResponse({
        "success": False,
        "message": message,
        "errors": errors
    }, status=status)

@csrf_exempt
def create_user(request):
    if request.method != "POST":
        return error_response("Only POST method allowed", status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return error_response("Invalid JSON")

    errors = {}
    required = ["username", "email", "password", "mobile", "role"]

    for field in required:
        if not data.get(field):
            errors[field] = f"{field} is required"

    if User.objects.filter(email=data.get("email")).exists():
        errors["email"] = "Email already exists"

    if errors:
        return error_response("Validation failed", errors)

    user = User.objects.create(
        username=data["username"],
        email=data["email"],
        password=make_password(data["password"]),
        mobile=data["mobile"],
        role=data["role"],
    )

    token = generate_access_token(user)

    return success_response(
        "User created successfully",
        {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "access_token": token,
        },
        201,
    )


@csrf_exempt
def login_user(request):
    if request.method != "POST":
        return error_response("Only POST method allowed", status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return error_response("Invalid JSON")

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return error_response("Email and password required")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return error_response("Invalid credentials", status=401)

    if not check_password(password, user.password):
        return error_response("Invalid credentials", status=401)

    token = generate_access_token(user)

    return success_response(
        "Login successful",
        {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "access_token": token,
        },
    )


OTP_EXPIRY_SECONDS = 300  # 5 minutes


@csrf_exempt
def send_otp(request):
    if request.method != "POST":
        return error_response("Only POST method allowed", status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return error_response("Invalid JSON")

    errors = {}

    send_by = data.get("sendBy")
    send_type = data.get("sendType")  # mobile / email
    send_for = data.get("sendFor")    # verification / forgot

    # -----------------------------
    # Validations (same as before)
    # -----------------------------
    if not send_by:
        errors["sendBy"] = "sendBy is required"

    if send_type not in ["mobile", "email"]:
        errors["sendType"] = "sendType must be mobile or email"

    if send_for not in ["verification", "forgot"]:
        errors["sendFor"] = "sendFor must be verification or forgot"

    if send_type == "mobile" and send_by:
        if not send_by.isdigit() or len(send_by) != 10:
            errors["sendBy"] = "Mobile must be 10 digits"

    if send_type == "email" and send_by:
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', send_by):
            errors["sendBy"] = "Invalid email format"

    if errors:
        return error_response("Validation failed", errors)

    # -----------------------------
    # Generate OTP
    # -----------------------------
    otp = random.randint(100000, 999999)
    created_at = int(time.time())



    # Delete old OTP for same user
    OTP.objects.filter(send_by=send_by).delete()

    # Save new OTP
    OTP.objects.create(
        send_by=send_by,
        send_type=send_type,
        send_for=send_for,
        otp=otp,
        created_at=created_at
    )
    if send_type == "mobile":
         print("mobile")
       
    #     sent = send_otp_sms(send_by, otp)
    else:
        sent = send_otp_email(send_by, otp)

    if not sent:
        return error_response("Failed to send OTP", status=500)


    return success_response(
        "OTP sent successfully",
        {
            "sendBy": send_by,
            "sendType": send_type,
            "sendFor": send_for,
            "otp": otp,  # ⚠️ show only for testing
            "expires_in": OTP_EXPIRY_SECONDS
        },
        201
    )



OTP_EXPIRY_SECONDS = 300  # 5 minutes


@csrf_exempt
def verify_otp(request):
    if request.method != "POST":
        return error_response("Only POST method allowed", status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return error_response("Invalid JSON")

    send_by = data.get("sendBy")
    send_type = data.get("sendType")
    send_for = data.get("sendFor")
    otp = data.get("otp")

    errors = {}

    # -------------------------
    # Validations
    # -------------------------
    if not send_by:
        errors["sendBy"] = "sendBy is required"

    if send_type not in ["mobile", "email"]:
        errors["sendType"] = "sendType must be mobile or email"

    if send_for not in ["verification", "forgot"]:
        errors["sendFor"] = "sendFor must be verification or forgot"

    if not otp:
        errors["otp"] = "OTP is required"

    if errors:
        return error_response("Validation failed", errors)

    # -------------------------
    # Find OTP in DB
    # -------------------------
    otp_obj = OTP.objects.filter(
        send_by=send_by,
        send_type=send_type,
        send_for=send_for,
        otp=otp
    ).first()

    if not otp_obj:
        return error_response("Invalid OTP", status=400)

    # -------------------------
    # Check expiry
    # -------------------------
    current_time = int(time.time())
    if current_time - otp_obj.created_at > OTP_EXPIRY_SECONDS:
        otp_obj.delete()
        return error_response("OTP expired", status=400)

    # OTP verified successfully → delete OTP
    otp_obj.delete()

    return success_response(
        "OTP verified successfully",
        {
            "sendBy": send_by,
            "sendType": send_type,
            "sendFor": send_for
        }
    )





@csrf_exempt
def get_all_users(request):
    if request.method != "GET":
        return error_response("Only GET method allowed", status=405)

    users = User.objects.all()

    if not users.exists():
        return success_response("No users found", [])

    users_list = []

    for user in users:
        users_list.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "mobile": user.mobile,
            "role": user.role,
        })

    return success_response(
        "Users fetched successfully",
        users_list
    )



@csrf_exempt
@admin_required
def get_users_by_role(request, role):
    if request.method != "GET":
        return error_response("Only GET allowed", status=405)

    users = User.objects.filter(role=role)

    data = [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "mobile": u.mobile,
            "role": u.role,
            "created_at": u.created_at,
        }
        for u in users
    ]

    return success_response(f"All {role}s fetched", data)

@csrf_exempt
@admin_required
def admin_create_user(request):
    if request.method != "POST":
        return error_response("Only POST allowed", status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return error_response("Invalid JSON")

    required = ["username", "email", "password", "mobile", "role"]
    errors = {}

    for field in required:
        if not data.get(field):
            errors[field] = f"{field} is required"

    if data.get("role") not in ["student", "teacher"]:
        errors["role"] = "Only student or teacher allowed"

    if User.objects.filter(email=data.get("email")).exists():
        errors["email"] = "Email already exists"

    if errors:
        return error_response("Validation failed", errors)

    user = User.objects.create(
        username=data["username"],
        email=data["email"],
        password=make_password(data["password"]),
        mobile=data["mobile"],
        role=data["role"],
    )

    return success_response(
        "User created successfully",
        {"id": user.id, "role": user.role},
        201
    )


@csrf_exempt
@admin_required
def admin_delete_user(request, user_id):
    if request.method != "DELETE":
        return error_response("Only DELETE allowed", status=405)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return error_response("User not found", status=404)

    user.delete()
    return success_response("User deleted successfully")




@csrf_exempt
@admin_required
def admin_update_user(request, user_id):
    if request.method != "PUT":
        return error_response("Only PUT allowed", status=405)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return error_response("User not found", status=404)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return error_response("Invalid JSON")

    user.username = data.get("username", user.username)
    user.mobile = data.get("mobile", user.mobile)

    if data.get("password"):
        user.password = make_password(data["password"])

    user.save()

    return success_response("User updated successfully")











@admin_required
def admin_list_teachers(request):
    if request.method != "GET":
        return error_response("Only GET allowed", status=405)

    teachers = User.objects.filter(role="teacher").values(
        "id",
        "username",
        "email",
        "mobile",
        "created_at"
    )

    return success_response("Teachers fetched", list(teachers))






