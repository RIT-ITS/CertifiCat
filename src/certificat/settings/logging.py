__all__ = ["LOGGING"]

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
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "huey": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "django": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "xmlschema": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False,
        },
        "acmev2": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}
