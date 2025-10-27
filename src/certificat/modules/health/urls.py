from . import views
from django.urls import path

app_name = "health"
urlpatterns = [
    path("healthz", views.healthz),
]
