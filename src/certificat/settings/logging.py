__all__ = ["LOGGING"]

import inject
from .dynamic import ApplicationSettings

dynamic_settings = inject.instance(ApplicationSettings)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "simple": {"format": "{asctime} {levelname} {message}", "style": "{"}
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "certificat": {
            "level": dynamic_settings.logging.certificat_level,
            "handlers": ["console"],
            "propagate": False,
        },
        "huey": {
            "level": dynamic_settings.logging.huey_level,
            "handlers": ["console"],
            "propagate": False,
        },
        "django": {
            "level": dynamic_settings.logging.django_level,
            "handlers": ["console"],
            "propagate": False,
        },
        "xmlschema": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False,
        },
        "acmev2": {
            "level": dynamic_settings.logging.acmev2_level,
            "handlers": ["console"],
            "propagate": False,
        },
    },
}
