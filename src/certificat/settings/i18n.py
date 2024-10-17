__all__ = ["LANGUAGE_CODE", "TIME_ZONE", "USE_I18N", "USE_L10N", "USE_TZ"]

from .dynamic import app_settings

LANGUAGE_CODE = "en-us"
TIME_ZONE = app_settings.time_zone
USE_I18N = True
USE_L10N = True
USE_TZ = True
