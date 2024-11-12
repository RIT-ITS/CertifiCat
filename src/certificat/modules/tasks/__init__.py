import logging

from certificat.settings.dynamic import ApplicationSettings
from huey.contrib.djhuey import task, db_task
import inject
from . import finalize_order
from . import validate_challenge
from . import housekeeping

logger = logging.getLogger(__name__)


@task()
def ping(pong_text: str) -> str:
    return pong_text


def deferred_task_setup():
    # defers setting up tasks because we need
    # app setting, which are only available after the
    # dependency injection container is setup.

    app_settings = inject.instance(ApplicationSettings)

    finalize_order.finalize_order_task = db_task(
        retries=app_settings.finalize_max_retries,
        retry_delay=app_settings.finalize_retry_delay,
        context=True,
    )(finalize_order.finalize_order_task)

    validate_challenge.validate_challenge_task = db_task(
        retries=app_settings.challenge_max_retries,
        retry_delay=app_settings.challenge_retry_delay,
        context=True,
    )(validate_challenge.validate_challenge_task)
