from datetime import timedelta
import logging
import time

from certificat.settings.dynamic import ApplicationSettings
from huey.contrib.djhuey import task, db_task, periodic_task
from huey import crontab
import inject
from . import finalize_order
from . import validate_challenge
from . import housekeeping  # noqa: F401
from . import beacon  # noqa: F401
from pathlib import Path

logger = logging.getLogger(__name__)


# The ping task must happen immediately or the app will be marked
# as unhealthy and may restart.
@task(priority=100)
def ping(pong_text: str) -> str:
    app_settings = inject.instance(ApplicationSettings)
    health_file = Path(app_settings.huey_health_file)
    health_file.touch()

    return pong_text


# Adds a ping task to the queue, make sure communication is happening
# between Huey and Redis
@periodic_task(crontab(minute="*"))
def pinger(task=None):
    cutoff = time.time() + 60
    while time.time() < cutoff:
        start = time.time()
        send_ping = ping("pong")
        send_ping(blocking=True)
        logger.debug(f"ping executed in {time.time() - start} seconds")

        time.sleep(10)


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
