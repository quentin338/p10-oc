from django.urls import path
from . import views


app_name = "core"

urlpatterns = [
    path('', views.legal_mentions, name="legal_mentions"),
]
