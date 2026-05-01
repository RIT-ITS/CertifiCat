from urllib.parse import urljoin

import inject
from .dynamic import ApplicationSettings

dynamic_settings = inject.instance(ApplicationSettings)

__all__ = [
    "LOGIN_URL",
    "LOGIN_REDIRECT_URL",
    "LOGOUT_REDIRECT_URL",
    "AUTHENTICATION_BACKENDS",
]

LOGIN_URL = urljoin(dynamic_settings.web_ui_mountpoint, "login/")
LOGIN_REDIRECT_URL = dynamic_settings.web_ui_mountpoint.rstrip("/") + "/"
LOGOUT_REDIRECT_URL = dynamic_settings.web_ui_mountpoint.rstrip("/") + "/"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

if dynamic_settings.authentication.type == "saml":
    LOGIN_URL = urljoin(dynamic_settings.web_ui_mountpoint, "saml2/login/")
    AUTHENTICATION_BACKENDS = ["certificat.auth.Saml2Backend"]
elif dynamic_settings.authentication.type == "remote":
    LOGIN_URL = urljoin(dynamic_settings.web_ui_mountpoint, "remote/login/")
    AUTHENTICATION_BACKENDS = ["certificat.auth.RemoteUserBackend"]

if not LOGIN_URL.startswith("/"):
    LOGIN_URL = "/" + LOGIN_URL
