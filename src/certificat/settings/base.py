import os

import inject
from .dynamic import ApplicationSettings

dynamic_settings = inject.instance(ApplicationSettings)

__all__ = [
    "BASE_DIR",
    "SECRET_KEY",
    "DEBUG",
    "ALLOWED_HOSTS",
    "APPEND_SLASH",
    "STATIC_URL",
    "STATIC_ROOT",
    "LOGIN_URL",
    "LOGIN_REDIRECT_URL",
    "LOGOUT_REDIRECT_URL",
    "AUTHENTICATION_BACKENDS",
    "INSTALLED_APPS",
    "MIDDLEWARE",
    "ROOT_URLCONF",
    "TEMPLATES",
    "WSGI_APPLICATION",
    "DEFAULT_AUTO_FIELD",
    "CSRF_TRUSTED_ORIGINS",
]


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = dynamic_settings.secret_key

DEBUG = dynamic_settings.debug

ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = [dynamic_settings.url_root]

APPEND_SLASH = False

STATIC_URL = "/static/"
STATIC_ROOT = dynamic_settings.staticfiles_root or os.path.join(
    BASE_DIR, "server/static"
)

SESSION_COOKIE_SECURE = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "djangosaml2",
    "huey.contrib.djhuey",
    "webpack_loader",
    "django_cotton",
    "certificat.app.CertificatConfig",
    "certificat.modules.acme",
    "certificat.modules.html",
    "certificat.modules.api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    # "csp.middleware.CSPMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "certificat.modules.html.middleware.global_request_middleware",
    "djangosaml2.middleware.SamlSessionMiddleware",
]

ROOT_URLCONF = "certificat.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "certificat.modules.html.context_processors.nav",
            ],
        },
    },
]

WSGI_APPLICATION = "certificat.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
