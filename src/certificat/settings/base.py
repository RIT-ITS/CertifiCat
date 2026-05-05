import os
from urllib.parse import urljoin

import inject
from .dynamic import ApplicationSettings

dynamic_settings = inject.instance(ApplicationSettings)

__all__ = [
    "ALLOWED_HOSTS",
    "APPEND_SLASH",
    "BASE_DIR",
    "CSRF_TRUSTED_ORIGINS",
    "DEBUG",
    "DEFAULT_AUTO_FIELD",
    "INSTALLED_APPS",
    "MIDDLEWARE",
    "ROOT_URLCONF",
    "SECRET_KEY",
    "SESSION_COOKIE_AGE",
    "SESSION_COOKIE_SECURE",
    "STATIC_ROOT",
    "STATIC_URL",
    "TEMPLATES",
    "WSGI_APPLICATION",
]


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = dynamic_settings.secret_key

DEBUG = False

ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = [dynamic_settings.url_root]


APPEND_SLASH = True

STATIC_URL = urljoin(dynamic_settings.web_ui_mountpoint, "static/")
STATIC_ROOT = dynamic_settings.staticfiles_root or os.path.join(
    BASE_DIR, "server/static"
)

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_AGE = dynamic_settings.session_cookie_age

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "djangosaml2",
    "huey.contrib.djhuey",
    "django_cotton",
    "import_export",
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
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "certificat.middleware.CustomHeaderRemoteUserMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "djangosaml2.middleware.SamlSessionMiddleware",
    "certificat.middleware.set_request_context",
]

ROOT_URLCONF = dynamic_settings.root_urlconf or "certificat.urls"

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
                "certificat.modules.html.context_processors.settings",
                "certificat.modules.html.context_processors.url_root",
                "certificat.modules.html.context_processors.version",
            ],
        },
    },
]

WSGI_APPLICATION = "certificat.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
