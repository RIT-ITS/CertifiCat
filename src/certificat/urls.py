from django.urls import include, path
import inject
from .settings import ApplicationSettings

app_settings = inject.instance(ApplicationSettings)

urlpatterns = [
    path("", include("certificat.modules.html.urls")),
    path("", include("certificat.modules.api.urls")),
    path("", include("certificat.modules.acme.urls")),
]

if app_settings.login_method == "saml":
    urlpatterns += [
        path("saml2/", include("djangosaml2.urls")),
    ]
