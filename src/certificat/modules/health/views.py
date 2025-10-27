import logging
from certificat.modules.tasks import ping
from django.http import HttpResponse

from certificat.settings.dynamic import ApplicationSettings
import inject

logger = logging.getLogger(__name__)


def healthz(request, *args, **argv):
    app_settings = inject.instance(ApplicationSettings)
    if (
        request.META["REMOTE_ADDR"] not in app_settings.healthcheck_allowed_ips
        and "*" not in app_settings.healthcheck_allowed_ips
    ):
        return HttpResponse(status=403)

    if test_huey():
        return HttpResponse("healthy")
    else:
        return HttpResponse("unhealthy", status=500)


def test_huey() -> bool:
    expected_pong_reply = "pong"
    pong_reply = ping(expected_pong_reply)

    return expected_pong_reply == pong_reply(blocking=True)
