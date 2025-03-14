import datetime
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from certificat.utils import unprefix_group
from lxml_html_clean import Cleaner
from certificat.modules.acme import models as db
from django.db.models import Count, DateField
from django.utils.dateformat import format
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone, dateparse
from django.db.models import Func
from django.views.decorators.cache import cache_page


class TruncDayNaive(Func):
    """Custom TruncDay implementation to avoid using timezone lookups
    on the server. We don't have those loaded and it's not necessary for
    the graph using this to have that level of fidelity anyway.
    """

    # TODO: Make sure other databases besides MySQL allow this format

    function = "DATE_FORMAT"
    template = "%(function)s(%(expressions)s, '%%%%Y-%%%%m-%%%%d')"
    output_field = DateField()

    def convert_value(self, value, expression, connection):
        return dateparse.parse_date(value)


@require_http_methods(["GET"])
@cache_page(60 * 15)  # Cached for 15 minutes
def cert_activity(request: HttpRequest):
    # 375 is not a typo, we get some extra days to account for the graph
    # winding back to the first Sunday of the week.
    start = timezone.now() - datetime.timedelta(days=375)
    activity = (
        db.Certificate.objects.filter(created_at__gt=start)
        .annotate(date=TruncDayNaive("created_at"))
        .values("date")
        .annotate(count=Count("id"))
        .values("date", "count")
    )
    return JsonResponse(
        {format(item["date"], "Y/m/d"): item["count"] for item in activity},
        safe=False,
    )


@login_required
@require_http_methods(["GET"])
def my_groups(request: HttpRequest):
    groups = request.user.groups.all().order_by("name").values("id", "name")
    # remove namespace prefixes from group names
    for group in groups:
        group["name"] = unprefix_group(group["name"])

    return JsonResponse(list(groups), safe=False)


@login_required
@csrf_exempt
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
