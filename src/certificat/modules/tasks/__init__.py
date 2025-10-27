import logging

from certificat.settings.dynamic import ApplicationSettings
from huey.contrib.djhuey import task, db_task
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

    if app_settings.beacon_enabled:
        logger.info(
            "A stat-gathering beacon has been enabled. This will send installed version, certificates issued per day, and a non-identifiable guid to RIT for usage data collection. To disable, set beacon_enabled to false in the config."
        )
    else:
        logger.info("Stat-gathering beacon disabled.")
