from typing import Any, Callable
import inject
from certificat.settings.dynamic import ApplicationSettings


from django.utils.functional import SimpleLazyObject


class LazyAppSetting(SimpleLazyObject):
    def __init__(
        self,
        func: Callable[
            [
                ApplicationSettings,
            ],
            Any,
        ],
    ):
        def get_setting():
            settings = inject.instance(ApplicationSettings)
            return func(settings)

        super().__init__(get_setting)
