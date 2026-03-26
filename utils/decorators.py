from functools import wraps
from django.http import JsonResponse

from django.http import JsonResponse
from utils.jwt import decode_access_token
from apps.users.models import User


def jwt_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user:
            return JsonResponse(
                {"success": False, "message": "Authentication required"},
                status=401
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user:
                return JsonResponse(
                    {"success": False, "message": "Authentication required"},
                    status=401
                )

            if request.user.role not in allowed_roles:
                return JsonResponse(
                    {"success": False, "message": "Permission denied"},
                    status=403
                )

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator




def teacher_or_admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse({"success": False, "message": "Token required"}, status=401)

        try:
            token = auth_header.split(" ")[1]
            payload = decode_access_token(token)
            user = User.objects.get(id=payload["user_id"])

            if user.role not in ["teacher", "admin"]:
                return JsonResponse(
                    {"success": False, "message": "Access denied"},
                    status=403
                )

            request.user = user

        except:
            return JsonResponse({"success": False, "message": "Invalid token"}, status=401)

        return view_func(request, *args, **kwargs)

    return wrapper










from django.http import JsonResponse
from utils.jwt import decode_access_token
from apps.users.models import User


def admin_required(view_func):

    def wrapper(request, *args, **kwargs):

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse({
                "success": False,
                "message": "Token required"
            }, status=401)

        try:
            token = auth_header.split(" ")[1]
            payload = decode_access_token(token)

            user = User.objects.get(id=payload["user_id"])

            if user.role != "admin":
                return JsonResponse({
                    "success": False,
                    "message": "Admin access required"
                }, status=403)

            request.user = user

        except Exception as e:
            return JsonResponse({
                "success": False,
                "message": str(e)
            }, status=401)

        return view_func(request, *args, **kwargs)

    return wrapper


def student_required(view_func):

    def wrapper(request, *args, **kwargs):

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse({
                "success": False,
                "message": "Token required"
            }, status=401)

        try:
            token = auth_header.split(" ")[1]

            payload = decode_access_token(token)

            user = User.objects.get(id=payload["user_id"])

            if user.role != "student":
                return JsonResponse({
                    "success": False,
                    "message": "Student access only"
                }, status=403)

            request.user = user

        except Exception:
            return JsonResponse({
                "success": False,
                "message": "Invalid or expired token"
            }, status=401)

        return view_func(request, *args, **kwargs)

    return wrapper