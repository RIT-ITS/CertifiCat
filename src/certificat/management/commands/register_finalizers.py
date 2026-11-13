import logging

import inject
from django.core.management.base import BaseCommand

from certificat.modules.acme import models as db
from certificat.modules.acme.finalizers import configured_finalizers
from certificat.settings.dynamic import ApplicationSettings

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Records thumbprints of the configured finalizers so changes to them are tracked"

    def handle(self, *args, **options):
        app_settings = inject.instance(ApplicationSettings)
        finalizers = configured_finalizers(app_settings)
        for finalizer in finalizers:
            record, created = db.FinalizerThumbprint.objects.register(finalizer)
            if created:
                logger.info(f"Registered new settings for finalizer {record}")
            else:
                logger.info(f"Finalizer {record} is unchanged")

        removed = db.FinalizerThumbprint.objects.deactivate_unconfigured(
            [f.short_name for f in finalizers]
        )
        if removed:
            logger.info(f"Deactivated {removed} finalizer(s) removed from the config")
