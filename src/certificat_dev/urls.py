import debug_toolbar
import inject
from django.urls import include, path

from certificat.settings.dynamic import ApplicationSettings

dynamic_settings = inject.instance(ApplicationSettings)


urlpatterns = [
    path("__debug__/", include(debug_toolbar.urls)),
    path("", include(dynamic_settings.root_urlconf or "certificat.urls")),
]
