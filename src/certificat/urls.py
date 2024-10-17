from django.urls import include, path

urlpatterns = [
    path("", include("certificat.modules.web.urls")),
    path("", include("certificat.modules.acme.urls")),
]
