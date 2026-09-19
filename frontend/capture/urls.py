from django.urls import path

from . import views

app_name = "capture"

urlpatterns = [
    path("", views.capture_view, name="capture"),
]
