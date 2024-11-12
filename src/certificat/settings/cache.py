__all__ = ["CACHES"]

import inject
from .dynamic import ApplicationSettings

dynamic_settings = inject.instance(ApplicationSettings)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://:{dynamic_settings.redis.password}@{dynamic_settings.redis.host}:{dynamic_settings.redis.port}",
        "OPTIONS": {"health_check_interval": 30},
    }
}
