import datetime
import json
import jwt

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import View

from common.constatnts.constants import (
    ACCESS_TYPE,
    REFRESH_TYPE,
    ACCESS_TOKEN_EXPIRY_MINUTES,
    REFRESH_TOKEN_EXPIRY_HOURS,
)
from common.forms import RetrieveTokenForm
from custom_users.models import CustomUser
from zone3000.settings import JWT_ALGORITHM, JWT_SECRET


@method_decorator(csrf_exempt, name="dispatch")
class BaseView(View):
    pass


class RetrieveTokenView(BaseView):
    @staticmethod
    def post(request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            form = RetrieveTokenForm(data)
            if not form.is_valid():
                return JsonResponse({"errors": form.errors}, status=400)

            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = CustomUser.objects.get(username=username)
            if not user.check_password(password):
                return JsonResponse({"error": "Invalid credentials"}, status=401)

            access_token_expiry = datetime.datetime.now() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES)
            refresh_token_expiry = datetime.datetime.now() + datetime.timedelta(days=REFRESH_TOKEN_EXPIRY_HOURS)

            access_payload = {
                "user_id": user.id,
                "username": user.username,
                "exp": access_token_expiry,
                "type": ACCESS_TYPE
            }
            refresh_payload = {
                "user_id": user.id,
                "exp": refresh_token_expiry,
                "type": REFRESH_TYPE
            }

            access_token = jwt.encode(
                access_payload,
                JWT_SECRET,
                algorithm=JWT_ALGORITHM
            )
            refresh_token = jwt.encode(
                refresh_payload,
                JWT_SECRET,
                algorithm=JWT_ALGORITHM
            )

            return JsonResponse({
                "access": access_token,
                "refresh": refresh_token,
                "username": user.username,
                "user_id": user.id
            })

        except CustomUser.DoesNotExist:
            return JsonResponse({"error": "Invalid credentials"}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
