import logging

from django.http import HttpRequest
from django.shortcuts import render

from certificat.modules.acme.models import (
    Certificate,
    Order,
)

from ..nav import Sections, build_breadcrumbs
from .base import ViewBase

logger = logging.getLogger(__name__)


class IndexView(ViewBase):
    section = Sections.Dashboard

    def get_breadcrumbs(self, **kwargs):
        return build_breadcrumbs("Home")

    def get(self, request: HttpRequest):
        recent_orders = Order.objects.by_user(request.user).recent()
        recent_certificates = Certificate.objects.recent()

        context = self.get_context_data(
            recent_orders=recent_orders, recent_certificates=recent_certificates
        )
        return render(request, "certificat/index.html", context)
