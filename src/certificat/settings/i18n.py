__all__ = ["LANGUAGE_CODE", "TIME_ZONE", "USE_I18N", "USE_L10N", "USE_TZ"]

import inject
from .dynamic import ApplicationSettings

dynamic_settings = inject.instance(ApplicationSettings)


LANGUAGE_CODE = "en-us"
TIME_ZONE = dynamic_settings.time_zone

USE_I18N = True
USE_L10N = True
USE_TZ = True
