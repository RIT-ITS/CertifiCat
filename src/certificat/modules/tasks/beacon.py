from datetime import timedelta
from django.utils import timezone
import logging
from certificat.settings.dynamic import ApplicationSettings
from huey.contrib.djhuey import db_periodic_task
from huey import crontab
import inject
from importlib.metadata import version
from certificat.modules.acme import models as db
import uuid
import requests

logger = logging.getLogger(__name__)


@db_periodic_task(crontab(minute="0", hour="*/12"))
def send_beacon():
    settings = inject.instance(ApplicationSettings)

    if not settings.beacon_enabled:
        logger.info("Skipping beacon, disabled in settings")
        return

    logger.info("Running beacon")
    app_version = version("certificat")
    beacon_guid = db.Config.get("beacon-guid")
    if not beacon_guid:
        beacon_guid = str(uuid.uuid4())
        db.Config.set("beacon-guid", beacon_guid)
    yesterday = timezone.now() - timedelta(days=1)
    certs_since_yesterday = db.Certificate.objects.filter(
        created_at__gte=yesterday
    ).count()

    params = {
        "version": app_version,
        "guid": beacon_guid,
        "certs_since_yesterday": certs_since_yesterday,
    }
    url = "https://certificat-beacon.rit.edu/"

    logger.info("Sending params %s to url %s", params, url)
    requests.get(url, params=params)
