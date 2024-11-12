from django.views.decorators.http import require_http_methods
from acmev2.services import IDirectoryService
from acmev2.handlers import (
    ACMERequestHandler,
    NewNonceRequestHandler,
    NewAccountRequestHandler,
    NewOrderRequestHandler,
    AuthorizationRequestHandler,
    ChallengeRequestHandler,
    OrderFinalizationRequestHandler,
    OrderRequestHandler,
    CertRequestHandler,
)
from acmev2.handlers import handle as process_acme_request
import inject
from django.http import HttpResponse, JsonResponse, HttpRequest
import json
from django.views.decorators.csrf import csrf_exempt


@require_http_methods(["GET"])
def directory(request):
    directory_service = inject.instance(IDirectoryService)
    return JsonResponse(
        directory_service.get_directory(), json_dumps_params={"indent": 4}
    )


def handleACMERequest(
    request: HttpRequest, ACMERequestType: ACMERequestHandler
) -> HttpResponse:
    body: str | None = None
    if request.method == "POST":
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            body = None

    req = ACMERequestType(
        request.build_absolute_uri(),
        request.method,
        request.headers,
        body,
    )

    acme_resp = process_acme_request(req)
    # Else must be set to blank string or Django will serialize the literal
    # None to "None" and then we'll have issues.
    resp_body = acme_resp.serialize() if acme_resp.msg else ""
    resp = HttpResponse(
        resp_body,
        status=acme_resp.code,
        headers=acme_resp.headers,
    )

    return resp


@csrf_exempt
def newNonce(request):
    return handleACMERequest(request, NewNonceRequestHandler)


@csrf_exempt
def newAccount(request):
    return handleACMERequest(request, NewAccountRequestHandler)


@csrf_exempt
def newOrder(request):
    return handleACMERequest(request, NewOrderRequestHandler)


@csrf_exempt
def authz(request, authz_id: str):
    return handleACMERequest(request, AuthorizationRequestHandler)


@csrf_exempt
def chall(request, chall_id: str):
    return handleACMERequest(request, ChallengeRequestHandler)


@csrf_exempt
def order(request, order_id: str):
    return handleACMERequest(request, OrderRequestHandler)


@csrf_exempt
def cert(request, cert_id: str):
    return handleACMERequest(request, CertRequestHandler)


@csrf_exempt
def finalize(request, order_id: str):
    return handleACMERequest(request, OrderFinalizationRequestHandler)
