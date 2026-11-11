import logging
from enum import Enum

import inject
from apprise import Apprise
from apprise.decorators import notify

from certificat.modules.acme import models as db
from certificat.settings.dynamic import ApplicationSettings, NotificationEventConfig

logger = logging.getLogger(__name__)


level_mapping = logging.getLevelNamesMapping()


@notify(on="stdout", name="Stdout Logger")
def stdout_logger(body: str, title: str, notify_type: str, *args, **kwargs):
    log_level = level_mapping.get(notify_type.upper(), level_mapping["INFO"])
    logger.log(log_level, f"{title} - {body}")


class Events(Enum):
    FINALIZATION_SUCCESS = "finalization-success"
    FINALIZATION_ERROR = "finalization-error"


class AppriseWrapper:
    def __init__(self, config: NotificationEventConfig | None):
        self.config = config

    def notify(
        self, body: str | bytes, title: str | bytes = "", *args, **kwargs
    ) -> bool | None:
        if self.config and self.config.enabled:
            apprise = Apprise()
            for service in self.config.services:
                apprise.add(service)

            return apprise.notify(body, title, *args, **kwargs)

        return True


def publish_finalization_success(order: db.Order):
    settings = inject.instance(ApplicationSettings)
    logger.debug("Publishing on_finalization_success notification")

    AppriseWrapper(settings.notifications.on_finalization_success).notify(
        f"Order {order.name} finalized successfully"
    )


def publish_finalization_error(order: db.Order):
    settings = inject.instance(ApplicationSettings)
    logger.debug("Publishing on_finalization_error notification")

    AppriseWrapper(settings.notifications.on_finalization_error).notify(
        f"Order {order.name} had an error during finalization"
    )
