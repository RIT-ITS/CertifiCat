import inject
from acmev2.settings import ACMESettings

from .dynamic import ApplicationSettings, LocalACMESettings

bindings = [
    (ApplicationSettings, ApplicationSettings.get()),
    (ACMESettings, LocalACMESettings.get()),
]

inject.configure(
    lambda binder: [binder.bind(api, impl) for api, impl in bindings],
    bind_in_runtime=False,
    once=True,
)

# Don't move this, the DI container must be configured before settings are accessed.
from .all import *
