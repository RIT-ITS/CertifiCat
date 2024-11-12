import json

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from lxml_html_clean import Cleaner
from certificat.modules.acme import models as db


@login_required
@require_http_methods(["GET"])
def my_groups(request: HttpRequest):
    groups = request.user.groups.all().values("id", "name")

    return JsonResponse(list(groups), safe=False)


@login_required
@require_http_methods(["POST"])
def edit_binding(request: HttpRequest, binding_name):
    binding = get_object_or_404(
        db.AccountBinding.objects.prefetch_related("group_scopes"),
        id=binding_name,
    )

    if not binding.accessible_by(request.user):
        return HttpResponse(status=403)

    request_json = json.loads(request.body)
    cleaner = Cleaner()
    cleaner.javascript = True
    cleaner.style = True

    if "name" in request_json:
        binding.name = request_json.get("name")

    if "note" in request_json:
        binding.note = request_json.get("note")

    if "groups" in request_json:
        groups = request_json["groups"]
        ids_to_remove = groups.get("del", [])
        ids_to_add = groups.get("add", [])

        binding.group_scopes.filter(group_id__in=ids_to_remove).delete()
        db.AccountBindingGroupScope.objects.bulk_create(
            [
                db.AccountBindingGroupScope(binding=binding, group_id=i)
                for i in ids_to_add
            ]
        )

    binding.save()

    return HttpResponse(status=200)
