__all__ = ["DATABASES"]

import inject
from .dynamic import ApplicationSettings

dynamic_settings = inject.instance(ApplicationSettings)

DATABASES = {"default": dynamic_settings.db.to_backend()}
