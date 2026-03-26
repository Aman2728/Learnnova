from django.http import JsonResponse
from utils.jwt import decode_access_token
from apps.users.models import User

class JWTAuthenticationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user = None

        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = decode_access_token(token)

            if payload:
                try:
                    request.user = User.objects.get(id=payload["user_id"])
                except User.DoesNotExist:
                    request.user = None

        return self.get_response(request)
