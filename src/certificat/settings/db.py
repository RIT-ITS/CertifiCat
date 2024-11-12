__all__ = ["DATABASES"]

import inject
from .dynamic import ApplicationSettings

dynamic_settings = inject.instance(ApplicationSettings)

DATABASES = {
    "default": {
        "ENGINE": dynamic_settings.db.engine,
        "NAME": dynamic_settings.db.name,
        "USER": dynamic_settings.db.user,
        "PASSWORD": dynamic_settings.db.password,
        "HOST": dynamic_settings.db.host,
        "PORT": dynamic_settings.db.port,
    }
}
