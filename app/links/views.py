import json

from django.http import JsonResponse

from common.api.decorators import jwt_access_required
from common.views import BaseView
from links.forms import UrlsForm, UrlsPatchForm
from links.models import RedirectRule


class UrlView(BaseView):
    @staticmethod
    @jwt_access_required
    def post(request, *args, **kwargs):
        try:
            user = request.user
            data = json.loads(request.body)
            form = UrlsForm(data)
            if not form.is_valid():
                return JsonResponse({"errors": form.errors}, status=400)

            redirect_url = form.cleaned_data.get("redirect_url")
            is_private = form.cleaned_data.get("is_private")

            redirect_rule = RedirectRule.objects.create(
                user=user,
                redirect_url=redirect_url,
                is_private=is_private,
            )

            return JsonResponse(
                redirect_rule.as_dict(),
                status=201,
                safe=False,
            )
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)


class UrlListView(BaseView):
    @staticmethod
    @jwt_access_required
    def get(request, *args, **kwargs):
        user = request.user
        redirect_rules = RedirectRule.objects.filter(user=user).select_related("user")
        return JsonResponse(
            [redirect_rule.as_dict() for redirect_rule in redirect_rules],
            status=200,
            safe=False,
        )


class UrlDetailView(BaseView):
    @staticmethod
    @jwt_access_required
    def get(request, redirect_rule_id, *args, **kwargs):
        user = request.user
        redirect_rule = RedirectRule.objects.get_by_id(redirect_rule_id, user)
        if not redirect_rule:
            return JsonResponse({"error": "RedirectRule not found"}, status=404)

        return JsonResponse(
            redirect_rule.as_dict(),
            status=200,
            safe=False,
        )

    @staticmethod
    @jwt_access_required
    def patch(request, redirect_rule_id, *args, **kwargs):
        try:
            user = request.user
            redirect_rule = RedirectRule.objects.get_by_id(redirect_rule_id, user)
            if not redirect_rule:
                return JsonResponse({"error": "RedirectRule not found"}, status=404)

            data = json.loads(request.body)
            form = UrlsPatchForm(data)
            if not form.is_valid():
                return JsonResponse({"errors": form.errors}, status=400)

            if "redirect_url" in data:
                redirect_rule.redirect_url = form.cleaned_data["redirect_url"]
            if "is_private" in data:
                redirect_rule.is_private = form.cleaned_data["is_private"]
            redirect_rule.save()

            return JsonResponse(
                redirect_rule.as_dict(),
                status=200,
                safe=False,
            )
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    @staticmethod
    @jwt_access_required
    def delete(request, redirect_rule_id, *args, **kwargs):
        user = request.user
        redirect_rule = RedirectRule.objects.get_by_id(redirect_rule_id, user)
        if not redirect_rule:
            return JsonResponse({"error": "RedirectRule not found"}, status=404)
        redirect_rule.delete()
        return JsonResponse({}, status=204)
