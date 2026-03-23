__all__ = ["CACHES"]

import inject
from .dynamic import ApplicationSettings

dynamic_settings = inject.instance(ApplicationSettings)

CACHES = {"default": dynamic_settings.cache.to_backend()}
