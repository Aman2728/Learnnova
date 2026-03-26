from django.http import JsonResponse
from utils.jwt import decode_access_token
from apps.users.models import User

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"success": False, "message": "Token required"}, status=401)

        try:
            token = auth_header.split(" ")[1]
            payload = decode_access_token(token)
            user = User.objects.get(id=payload["user_id"])

            if user.role != "admin":
                return JsonResponse({"success": False, "message": "Admin only"}, status=403)

            request.admin = user
        except Exception:
            return JsonResponse({"success": False, "message": "Invalid token"}, status=401)

        return view_func(request, *args, **kwargs)
    return wrapper
