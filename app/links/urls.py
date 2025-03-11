from django.urls import path

from links.views import UrlView, UrlListView, UrlDetailView

urlpatterns = [
    path("", UrlView.as_view()),
    path("redirect_rules", UrlListView.as_view()),
    path("<str:redirect_rule_id>", UrlDetailView.as_view()),
]
