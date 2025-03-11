from django.contrib import admin
from django.urls import path

from common.views import RetrieveTokenView

urlpatterns = [
    path('retrieve-token/', RetrieveTokenView.as_view(), name='retrieve_token'),
]
