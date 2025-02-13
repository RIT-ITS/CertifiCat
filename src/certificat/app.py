from django.apps import AppConfig
from certificat.settings import bindings as settings_bindings
from django.db.models.signals import class_prepared
import inject


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

        import inject

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
        return super().ready()


def add_db_prefix(sender, **kwargs):
    from certificat.settings.dynamic import ApplicationSettings

    settings = inject.instance(ApplicationSettings)
    if settings.db.table_prefix:
        sender._meta.db_table = settings.db.table_prefix + sender._meta.db_table


class_prepared.connect(add_db_prefix)
