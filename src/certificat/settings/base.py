import os

from .lazy import LazyAppSetting

__all__ = [
    "BASE_DIR",
    "SECRET_KEY",
    "DEBUG",
    "ALLOWED_HOSTS",
    "APPEND_SLASH",
    "STATIC_URL",
    "STATIC_ROOT",
    "LOGOUT_REDIRECT_URL",
    "AUTHENTICATION_BACKENDS",
    "INSTALLED_APPS",
    "MIDDLEWARE",
    "ROOT_URLCONF",
    "TEMPLATES",
    "WSGI_APPLICATION",
    "DEFAULT_AUTO_FIELD",
]


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = LazyAppSetting(lambda settings: settings.secret_key)

DEBUG = LazyAppSetting(lambda settings: settings.debug)

ALLOWED_HOSTS = ["*"]

APPEND_SLASH = False

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "server/static")

LOGOUT_REDIRECT_URL = "/logout-successful/"

AUTHENTICATION_BACKENDS = []  # "acme_proxy.server.auth.Saml2Backend"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # "djangosaml2",
    "huey.contrib.djhuey",
    # "webpack_loader",
    "certificat.app.CertificatConfig",
    "certificat.modules.acme",
    "certificat.modules.web",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # 'django.middleware.csrf.CsrfViewMiddleware',
    # "csp.middleware.CSPMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # "djangosaml2.middleware.SamlSessionMiddleware",
    # "acme_proxy.server.middleware.GlobalRequestMiddleware",
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
            ],
        },
    },
]

WSGI_APPLICATION = "certificat.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
