import logging
from certificat.modules.tasks import ping
from django.http import HttpResponse

from certificat.settings.dynamic import ApplicationSettings
import inject
import ipaddress

logger = logging.getLogger(__name__)


def can_access_healthcheck(request) -> bool:
    app_settings = inject.instance(ApplicationSettings)
    for ip in app_settings.healthcheck_allowed_networks:
        if ip == "*":
            return True

        ip_address = ipaddress.ip_address(request.META["REMOTE_ADDR"])
        network = ipaddress.ip_network(ip, strict=False)

        if ip_address in network:
            return True

    return False


def healthz(request, *args, **argv):
    if can_access_healthcheck(request):
        if test_huey():
            return HttpResponse("healthy")
        else:
            return HttpResponse("unhealthy", status=500)

    return HttpResponse(status=403)


def test_huey() -> bool:
    expected_pong_reply = "pong"
    pong_reply = ping(expected_pong_reply)

    return expected_pong_reply == pong_reply(blocking=True)
