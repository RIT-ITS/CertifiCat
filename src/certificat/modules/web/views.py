from django.http import JsonResponse

from certificat.modules.acme.models import to_pydantic


def index(request):
    from certificat.modules.acme.models import Account, Order

    acct = Account.objects.first()
    order = Order.objects.last()
    res = to_pydantic(order.authorizations.first())

    return JsonResponse(res.model_dump(), json_dumps_params={"indent": 2})
