from django.urls import path

from redirects.views import PrivateRedirectView, PublicRedirectView

urlpatterns = [
    path('public/<str:redirect_identifier>', PublicRedirectView.as_view()),
    path('private/<str:redirect_identifier>',  PrivateRedirectView.as_view()),
]
