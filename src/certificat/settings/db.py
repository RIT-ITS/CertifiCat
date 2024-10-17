import inject
from .dynamic import ApplicationSettings
from django.utils.functional import SimpleLazyObject

__all__ = ["DATABASES"]


def _default_database():
    app_settings = inject.instance(ApplicationSettings)
    return {
        "ENGINE": app_settings.db.engine,
        "NAME": app_settings.db.name,
        "USER": app_settings.db.user,
        "PASSWORD": app_settings.db.password,
        "HOST": app_settings.db.host,
        "PORT": app_settings.db.port,
    }


DATABASES = {"default": SimpleLazyObject(_default_database)}
