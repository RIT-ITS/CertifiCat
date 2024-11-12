import inject
from .dynamic import ApplicationSettings
from acmev2.settings import ACMESettings

bindings = [
    (ApplicationSettings, ApplicationSettings()),
    (ACMESettings, ACMESettings()),
]

inject.configure(
    lambda binder: [binder.bind(api, impl) for api, impl in bindings],
    bind_in_runtime=False,
    once=True,
)

# Don't move this, the DI container must be configured before settings are accessed.
# Is using the DI container for settings wise? I don't know.

from .all import *  # noqa: F403, E402
