from django.urls import include, path, re_path
from django.views.generic.base import RedirectView

from certificat.settings.dynamic import ApplicationSettings
from .modules.acme.views import directory

app_settings = ApplicationSettings.get()

if app_settings.web_acme_mountpoint == app_settings.DEFAULT_ACME_MOUNTPOINT:
    acme_directory = "directory"
else:
    acme_directory = app_settings.web_acme_mountpoint + "directory"

urlpatterns = [
    path(app_settings.web_ui_mountpoint, include("certificat.modules.html.urls")),
    path(app_settings.web_api_mountpoint, include("certificat.modules.api.urls")),
    path(app_settings.web_acme_mountpoint, include("certificat.modules.acme.urls")),
    # This intentionally does not use the acme root mount point. We need to have one and only
    # one directory URL since clients can use that URL to store credentials.
    re_path(acme_directory + r"/?$", directory, name="directory"),
    path("health/", include("certificat.modules.health.urls")),
    path(
        "feedback",
        RedirectView.as_view(
            url="https://forms.gle/Mm4mLqscLJ4XwQnN7", permanent=False
        ),
        name="feedback",
    ),
]

handler404 = "certificat.modules.html.views.handler404"
handler500 = "certificat.modules.html.views.handler500"
