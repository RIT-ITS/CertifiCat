import logging

from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from certificat.modules.acme.models import (
    AccountBinding,
    Certificate,
)

from ..nav import Sections, build_breadcrumbs
from .base import ViewBase

logger = logging.getLogger(__name__)


class CertificatesView(ViewBase):
    section = Sections.Certificates

    def get_context_data(self, **kwargs):
        return super().get_context_data(certificates=self.get_certificates(), **kwargs)

    def get_breadcrumbs(self, **kwargs):
        return build_breadcrumbs("Certificates")

    def get_certificates(self):
        certificates_queryset = Certificate.objects.search(
            self.request.GET.get("filter")
        )
        certificates_paginator, certificates_page = certificates_queryset.paginated(
            self.request.GET.get("page", 1)
        )

        return {
            "paginator": certificates_paginator,
            "page": certificates_page,
        }

    def get(self, request):
        context = self.get_context_data()

        return render(request, "certificat/certificates.html", context)


class CertificateView(ViewBase):
    section = Sections.Certificates

    def get_breadcrumbs(self, **kwargs):
        return build_breadcrumbs(
            ("Certificates", reverse(Sections.Certificates.value)), "Detail"
        )

    def get(self, request: HttpRequest, cert_id: int):
        cert = get_object_or_404(
            Certificate.objects.select_related("order__account__binding"), pk=cert_id
        )
        user_can_access_binding = False
        try:
            user_can_access_binding = cert.order.account.binding.accessible_by(
                request.user
            )
        except AccountBinding.DoesNotExist:
            user_can_access_binding = False

        context = self.get_context_data(
            cert=cert,
            user_can_access_order=user_can_access_binding,
        )

        return render(request, "certificat/certificate.html", context)
