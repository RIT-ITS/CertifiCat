import inject
from .all import *  # noqa: F403


from .dynamic import ApplicationSettings, ACMESettings

bindings = [
    (ApplicationSettings, ApplicationSettings()),
    (ACMESettings, ACMESettings()),
]

inject.configure(
    lambda binder: [binder.bind(api, impl) for api, impl in bindings],
    bind_in_runtime=False,
    once=True,
)
