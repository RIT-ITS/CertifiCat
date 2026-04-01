from django.core.management.base import BaseCommand
from certificat.settings.dynamic import ApplicationSettings, LocalAuthSettings
import inject
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Runs any initialization commands before the server starts"

    def handle(self, *args, **options):
        settings = inject.instance(ApplicationSettings)
        if settings.authentication.type == "local":
            User = get_user_model()
            auth_settings: LocalAuthSettings = settings.authentication
            if User.objects.filter(username=auth_settings.admin.username).exists():
                user = User.objects.get(username=auth_settings.admin.username)
                user.username = auth_settings.admin.username
                user.email = auth_settings.admin.email
                user.set_password(auth_settings.admin.password)
                user.save()

                logger.info("Local admin user updated")
            else:
                User.objects.create_superuser(
                    auth_settings.admin.username,
                    auth_settings.admin.email,
                    auth_settings.admin.password,
                )

                logger.info("Local admin user created")
