from django.apps import AppConfig


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

        bindings = [
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
            once=True,
        )

        # Import tasks to register them and make them available to call
        import certificat.modules.tasks  # noqa: F401

        certificat.modules.tasks.deferred_task_setup()
        return super().ready()
