import inject
from .dynamic import ApplicationSettings

dynamic_settings = inject.instance(ApplicationSettings)

__all__ = [
    "LOGIN_URL",
    "LOGIN_REDIRECT_URL",
    "LOGOUT_REDIRECT_URL",
    "AUTHENTICATION_BACKENDS",
]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

if dynamic_settings.authentication.type == "saml":
    LOGIN_URL = "/saml2/login/"
    AUTHENTICATION_BACKENDS = ["certificat.auth.Saml2Backend"]
elif dynamic_settings.authentication.type == "remote":
    LOGIN_URL = "/remote/login/"
    AUTHENTICATION_BACKENDS = ["certificat.auth.RemoteUserBackend"]
