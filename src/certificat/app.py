from django.apps import AppConfig
from certificat.settings import bindings as settings_bindings
from django.db.models.signals import class_prepared
from certificat.settings.dynamic import ApplicationSettings
import inject
from acmev2.settings import ACMESettings
import logging
import os
from certificat import __version__

logger = logging.getLogger(__name__)


class CertificatConfig(AppConfig):
    name = "certificat"
    verbose_name = "certificat"

    def ready(self):
        # Imports are in ready to respect Django lifecycle.
        # This only happens once and it happens on app startup,
        # so the performance hit is low.
        from acmev2.services import (
            INonceService,
            IDirectoryService,
            IAccountService,
            IOrderService,
            IAuthorizationService,
            IChallengeService,
            ICertService,
        )

        from certificat.modules.acme.services import (
            NonceService,
            DirectoryService,
            AccountService,
            OrderService,
            AuthorizationService,
            ChallengeService,
            CertService,
        )

        # Re-binds instances to the injector. Since it can only happen once
        # it needs to get the settings bindings and re-apply them.
        bindings = settings_bindings + [
            (INonceService, NonceService()),
            (IDirectoryService, DirectoryService()),
            (IAccountService, AccountService()),
            (IOrderService, OrderService()),
            (IAuthorizationService, AuthorizationService()),
            (IChallengeService, ChallengeService()),
            (ICertService, CertService()),
        ]

        inject.configure(
            lambda binder: [binder.bind(api, impl) for api, impl in bindings],
            bind_in_runtime=False,
            clear=True,
        )

        # Import tasks to register them and make them available to call
        import certificat.modules.tasks  # noqa: F401

        certificat.modules.tasks.deferred_task_setup()

        acme_settings = inject.instance(ACMESettings)
        app_settings = inject.instance(ApplicationSettings)

        if (
            os.environ.get("RUN_MAIN") == "true"
            or os.environ.get("DJANGO_WSGI") == "true"
        ):
            if app_settings.beacon_enabled:
                logger.info(
                    "A stat-gathering beacon has been enabled. This will send installed version, certificates issued per day, and a non-identifiable guid to RIT for usage data collection. To disable, set beacon_enabled to false in the config."
                )
            else:
                logger.info("Stat-gathering beacon disabled.")

            if not acme_settings.eab_required:
                logger.warning(
                    "Forcing external account binding to True. CertifiCat can not run with anonymous account binding. To suppress this message set the acme.eab_required flag to True in your config."
                )
                acme_settings.eab_required = True

            try:
                deprecations = app_settings.get_deprecations()
                if deprecations:
                    logger.warning(
                        "You have deprecated settings. These settings will be removed in the future. Please take action to ensure the service will start when updates are applied."
                    )
                    for deprecation in deprecations:
                        logger.warning(deprecation)
            except Exception:
                logger.exception("Error getting setting deprecations")

            logger.info(
                "CertifiCat has completed initialization and is ready. Version: "
                + __version__
            )

        return super().ready()


def add_db_prefix(sender, **kwargs):
    from certificat.settings.dynamic import ApplicationSettings

    settings = inject.instance(ApplicationSettings)
    try:
        if settings.db.table_prefix:
            sender._meta.db_table = settings.db.table_prefix + sender._meta.db_table
    except AttributeError:
        pass


class_prepared.connect(add_db_prefix)
