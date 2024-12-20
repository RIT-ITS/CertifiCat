import json
from typing import Any
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse
from django.views.generic.base import ContextMixin
from django.views import View
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator, EmptyPage
from certificat.modules.acme.models import (
    Certificate,
    Order,
    AccountBinding,
    AccountEventType,
    OrderEventType,
    TempUsageHack,
)
from certificat.modules.html.forms import NewBindingForm
from certificat.settings.dynamic import ApplicationSettings, SAMLSettings
import inject
from .nav import BreadCrumb, BreadCrumbs, build_breadcrumbs, Sections
from django.contrib import messages
import logging
from acmev2.models import AccountStatus
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q


logger = logging.getLogger(__name__)


class ViewBase(UserPassesTestMixin, ContextMixin, View):
    settings: ApplicationSettings = inject.attr(ApplicationSettings)

    def test_func(self):
        return self.request.user.is_authenticated

    def get_breadcrumbs(self) -> BreadCrumbs:
        return BreadCrumbs()

    def get_context_data(self, **kwargs):
        return super().get_context_data(breadcrumbs=self.get_breadcrumbs(), **kwargs)

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return render(self.request, "certificat/no-permission.html", status=403)
        else:
            return super().handle_no_permission()


class IndexView(ViewBase):
    section = Sections.Dashboard

    def get_breadcrumbs(self):
        return build_breadcrumbs("Home")

    def get(self, request):
        recent_orders = (
            Order.objects.by_user(request.user)
            .order_by("-created_at")
            .prefetch_related("identifiers")[:10]
        )
        recent_certificates = Certificate.objects.all().order_by("-created_at")[:10]

        context = self.get_context_data(
            recent_orders=recent_orders, recent_certificates=recent_certificates
        )
        return render(request, "certificat/index.html", context)


class UsageView(ViewBase):
    section = Sections.Usage

    def get_breadcrumbs(self):
        return build_breadcrumbs("Usage")

    def get(self, request):
        context = self.get_context_data(
            text=TempUsageHack.objects.order_by("-created_at").first()
        )
        return render(request, "certificat/usage.html", context)


class TermsOfService(ViewBase):
    section = Sections.TOS

    def get_breadcrumbs(self):
        return build_breadcrumbs("Terms of Service")

    def get(self, request):
        context = self.get_context_data()
        return render(request, "certificat/terms-of-service.html", context)


class AccountsView(ViewBase):
    section = Sections.Accounts

    def get_context_data(self, **kwargs):
        return super().get_context_data(bindings=self.get_bindings(), **kwargs)

    def get_breadcrumbs(self):
        return build_breadcrumbs("Accounts")

    def get_bindings(self):
        bindings_queryset = (
            AccountBinding.objects.by_user(self.request.user)
            .filter(Q(bound_to=None) | Q(bound_to__status=AccountStatus.valid))
            .select_related("bound_to", "creator")
            .prefetch_related("group_scopes", "group_scopes__group")
            .order_by("-created_at")
        )
        bindings_paginator = Paginator(bindings_queryset, 20)
        try:
            bindings_page = bindings_paginator.page(self.request.GET.get("page", 1))
        except EmptyPage:
            bindings_page = bindings_paginator.page(1)

        return {
            "paginator": bindings_paginator,
            "page": bindings_page,
        }

    def get(self, request):
        new_binding_form = NewBindingForm(request.user, label_suffix="")
        context = self.get_context_data(new_binding_form=new_binding_form)

        return render(request, "certificat/accounts.html", context)

    def post(self, request):
        new_binding_form = NewBindingForm(request.user, request.POST)
        context = self.get_context_data(new_binding_form=new_binding_form)

        if new_binding_form.is_valid():
            try:
                binding = new_binding_form.save(request)
                return HttpResponseRedirect(reverse("account", args=[binding.id]))
            except:  # noqa: E722
                messages.error(request, "There was an error creating your binding.")
                logger.exception("Error creating new binding")

        return render(request, "certificat/accounts.html", context)


class AccountView(ViewBase):
    section = Sections.Accounts

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(**kwargs)

    def get_breadcrumbs(self):
        return build_breadcrumbs(
            ("Accounts", reverse(Sections.Accounts.value)), "Details"
        )

    def dispatch(self, request, binding_id, *args, **kwargs):
        binding = get_object_or_404(
            AccountBinding.objects.prefetch_related("group_scopes").select_related(
                "creator",
            ),
            id=binding_id,
        )

        if not binding.accessible_by(request.user):
            return self.handle_no_permission()

        return super().dispatch(request, binding=binding, *args, **kwargs)

    def post(self, request, binding: AccountBinding):
        if "revoke-account" in request.POST:
            binding.bound_to.revoke()
            messages.info(request, "The account was successfully revoked.")

        if "delete-binding" in request.POST:
            if binding.bound_to:
                messages.error(request, "Can't delete a binding with an account.")
            else:
                binding.delete()
                messages.info(request, "The binding was successfully deleted.")
                return HttpResponseRedirect(reverse(Sections.Accounts.value))

        return HttpResponseRedirect(reverse("account", args=[binding.id]))

    def get(self, request, binding: AccountBinding, *args, **kwargs):
        orders = Order.objects.filter(account=binding.bound_to).order_by("-created_at")
        binding_event = (
            binding.bound_to.events.filter(event_type=AccountEventType.BOUND).first()
            if binding.bound_to
            else None
        )
        context = self.get_context_data(
            binding=binding,
            binding_event=binding_event,
            access_group_json=json.dumps(
                [
                    {"id": g.group.id, "name": g.group.name}
                    for g in binding.group_scopes.all().order_by("group__name")
                ]
            ),
            orders=orders[:10],
            account_invalid=binding.bound_to
            and binding.bound_to.status != AccountStatus.valid,
        )

        template = "certificat/account.html"
        if not binding.bound_to:
            template = "certificat/account.activate.html"
        return render(request, template, context)


class OrderView(ViewBase):
    section = Sections.Accounts

    def get_breadcrumbs(self):
        return build_breadcrumbs(
            ("Accounts", reverse(Sections.Accounts.value)), "Order Detail"
        )

    def get(self, request, order_id):
        order = get_object_or_404(
            Order.objects.select_related(
                "account", "account__binding"
            ).prefetch_related(
                "authorizations",
                "authorizations__identifier",
                "authorizations__challenges",
                "authorizations__challenges__errors",
                "identifiers",
            ),
            id=order_id,
        )
        if not order.account.binding.accessible_by(request.user):
            return self.handle_no_permission()

        creation_event = order.events.filter(event_type=OrderEventType.CREATED).first()
        context = self.get_context_data(order=order, creation_event=creation_event)
        return render(request, "certificat/order.html", context)


class CertificatesView(ViewBase):
    section = Sections.Certificates

    def get_context_data(self, **kwargs):
        return super().get_context_data(certificates=self.get_certificates(), **kwargs)

    def get_breadcrumbs(self):
        return build_breadcrumbs("Certificates")

    def get_certificates(self):
        certificates_queryset = Certificate.objects.order_by("-created_at")
        certificates_paginator = Paginator(certificates_queryset, 20)
        try:
            certificates_page = certificates_paginator.page(
                self.request.GET.get("page", 1)
            )
        except EmptyPage:
            certificates_page = certificates_paginator.page(1)

        return {
            "paginator": certificates_paginator,
            "page": certificates_page,
        }

    def get(self, request):
        context = self.get_context_data()

        return render(request, "certificat/certificates.html", context)


class CertificateView(ViewBase):
    section = Sections.Certificates

    def get_breadcrumbs(self):
        return build_breadcrumbs(
            ("Certificates", reverse(Sections.Certificates.value)), "Detail"
        )

    def get(self, request, cert_id):
        cert = get_object_or_404(Certificate, pk=cert_id)
        context = self.get_context_data(cert=cert)

        return render(request, "certificat/certificate.html", context)


class LocalLoginView(LoginView):
    breadcrumbs = BreadCrumbs([BreadCrumb("Certificat", "/"), BreadCrumb("Login")])

    def get_context_data(self, **kwargs):
        return super().get_context_data(breadcrumbs=self.breadcrumbs, **kwargs)


class LocalLogoutView(LogoutView):
    http_method_names = ["get", "post", "options"]
    breadcrumbs = BreadCrumbs([BreadCrumb("Certificat", "/"), BreadCrumb("Logout")])

    def get_context_data(self, **kwargs):
        return super().get_context_data(breadcrumbs=self.breadcrumbs, **kwargs)

    def get(self, request, *args, **kwargs):
        from django.contrib.auth import logout as auth_logout

        auth_logout(request)
        context = self.get_context_data()
        return render(request, "certificat/logout.html", context=context)


def acs_failure(request, exception, status, **kwargs):
    attributes = kwargs.get("session_info", {}).get("ava")
    logger.exception(exception)
    logger.info(kwargs)

    return render(
        request,
        "certificat/acs_error.html",
        {
            "attributes": attributes,
            "exception": exception,
            "saml_settings": SAMLSettings.get(),
        },
    )
