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
if DEBUG:
    DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda *args, **kwargs: False}
