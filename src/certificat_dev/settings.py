from certificat.settings import *  # noqa: F403

DEBUG = True
WEBPACK_LOADER["DEFAULT"]["CACHE"] = False
INSTALLED_APPS += [
    "debug_toolbar",
]
MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]
ROOT_URLCONF = "certificat_dev.urls"
VITE_HOST = "certificat-vite.dev.localhost"
VITE_PORT = 443

if DEBUG:
    DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda *args, **kwargs: True}
