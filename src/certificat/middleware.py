from certificat.modules.html.contextvars import request_context
from django.contrib.auth.middleware import RemoteUserMiddleware
import logging

from certificat.settings.dynamic import ApplicationSettings
import inject

logger = logging.getLogger(__name__)


def set_request_context(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        request_context.set(request)

        response = get_response(request)

        return response

    return middleware


class CustomHeaderRemoteUserMiddleware(RemoteUserMiddleware):
    app_settings = inject.attr(ApplicationSettings)

    def process_request(self, request):
        if self.app_settings.authentication.type == "remote":
            self.header = self.app_settings.authentication.user_header
            self.force_logout_if_no_header = (
                self.app_settings.authentication.force_logout_if_no_header
            )

            logger.debug("Checking for %s header in request", self.header)
            return super().process_request(request)

        return
