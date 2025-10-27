import logging
from certificat.modules.tasks import ping
from django.http import HttpResponse

from certificat.settings.dynamic import ApplicationSettings
import inject
import ipaddress

logger = logging.getLogger(__name__)


def can_access_healthcheck(request) -> bool:
    app_settings = inject.instance(ApplicationSettings)
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        request_ip = x_forwarded_for.split(",")[0]
    else:
        request_ip = request.META.get("REMOTE_ADDR")

    for ip in app_settings.healthcheck_allowed_networks:
        if ip == "*":
            return True

        request_ip_address = ipaddress.ip_address(request_ip)
        network = ipaddress.ip_network(ip, strict=False)

        if request_ip_address in network:
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
