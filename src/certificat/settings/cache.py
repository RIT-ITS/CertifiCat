from django.utils.functional import SimpleLazyObject
from .dynamic import ApplicationSettings

import inject

__all__ = ["CACHES"]


def _default_cache():
    app_settings = inject.instance(ApplicationSettings)
    return {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://:{app_settings.redis.password}@{app_settings.redis.host}:{app_settings.redis.port}",
        "OPTIONS": {"health_check_interval": 30},
    }


CACHES = {"default": SimpleLazyObject(_default_cache)}
