from functools import wraps
import jwt
from django.http import JsonResponse
from django.contrib.auth.models import User

from common.constatnts.constants import ACCESS_TYPE
from custom_users.models import CustomUser
from zone3000.settings import JWT_ALGORITHM, JWT_SECRET


def jwt_access_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization", '')

        if not auth_header.startswith("Bearer ") and not auth_header.startswith("Token "):
            return JsonResponse({"error": "Authorization header must start with Bearer or Token"}, status=401)

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(
                token,
                JWT_SECRET,
                JWT_ALGORITHM
            )

            if payload.get("type") != ACCESS_TYPE:
                return JsonResponse({"error": "Invalid token type"}, status=401)

            user_id = payload.get("user_id")
            request.user = CustomUser.objects.get(id=user_id)

            return view_func(request, *args, **kwargs)

        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "Token expired"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"error": "Invalid token"}, status=401)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=401)

    return wrapper
