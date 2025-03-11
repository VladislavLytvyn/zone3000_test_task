from django.http import JsonResponse

from common.api.decorators import jwt_access_required
from common.views import BaseView
from links.models import RedirectRule


class PrivateRedirectView(BaseView):
    @staticmethod
    @jwt_access_required
    def get(request, redirect_identifier, *args, **kwargs):
        redirect_rule = RedirectRule.objects.get_by_identifier(redirect_identifier)
        if not redirect_rule:
            return JsonResponse({"error": "RedirectRule not found"}, status=404)

        return JsonResponse(
            redirect_rule.as_dict(),
            status=302,
            safe=False,
        )


class PublicRedirectView(BaseView):
    @staticmethod
    def get(request, redirect_identifier, *args, **kwargs):
        redirect_rule = RedirectRule.objects.get_by_identifier(redirect_identifier)
        if not redirect_rule or redirect_rule.is_private:
            return JsonResponse({"error": "RedirectRule not found"}, status=404)

        return JsonResponse(
            redirect_rule.as_dict(),
            status=302,
            safe=False,
        )