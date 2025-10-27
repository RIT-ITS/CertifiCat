from django.urls import include, path
import inject
from .settings import ApplicationSettings
from django.views.generic.base import RedirectView

app_settings = inject.instance(ApplicationSettings)

urlpatterns = [
    path("", include("certificat.modules.html.urls")),
    path("", include("certificat.modules.api.urls")),
    path("", include("certificat.modules.acme.urls")),
    path("health/", include("certificat.modules.health.urls")),
    path(
        "feedback",
        RedirectView.as_view(
            url="https://forms.gle/Mm4mLqscLJ4XwQnN7", permanent=False
        ),
        name="feedback",
    ),
]

if app_settings.login_method == "saml":
    urlpatterns += [
        path("saml2/", include("djangosaml2.urls")),
    ]

handler404 = "certificat.modules.html.views.handler404"
handler500 = "certificat.modules.html.views.handler500"
