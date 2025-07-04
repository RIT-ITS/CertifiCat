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
    TermsOfService,
    Usage,
)
from certificat.modules.html.forms import (
    NewBindingForm,
    TermsOfServiceEditForm,
    UsageEditForm,
)
from certificat.settings.dynamic import ApplicationSettings, SAMLSettings
from certificat.utils import unprefix_group
import inject
from .nav import BreadCrumb, BreadCrumbs, build_breadcrumbs, Sections
from django.contrib import messages
import logging
from acmev2.models import AccountStatus
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
import markdown

logger = logging.getLogger(__name__)


class ViewBase(UserPassesTestMixin, ContextMixin, View):
    settings: ApplicationSettings = inject.attr(ApplicationSettings)

    def test_func(self):
        return self.request.user.is_authenticated

    def get_breadcrumbs(self, **kwargs) -> BreadCrumbs:
        return BreadCrumbs()

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            breadcrumbs=self.get_breadcrumbs(**kwargs), **kwargs
        )

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return render(self.request, "certificat/no-permission.html", status=403)
        else:
            return super().handle_no_permission()


class IndexView(ViewBase):
    section = Sections.Dashboard

    def get_breadcrumbs(self, **kwargs):
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

    def get_breadcrumbs(self, **kwargs):
        return build_breadcrumbs("Usage")

    def get(self, request):
        # TODO: Maybe cache this

        last_usage = Usage.objects.order_by("-created_at").first()
        parsed_markdown = ""
        if last_usage:
            parsed_markdown = markdown.markdown(last_usage.text)
        context = self.get_context_data(
            text=parsed_markdown,
            can_edit=request.user.is_superuser,
        )
        return render(request, "certificat/usage.html", context)


class EditUsageView(ViewBase):
    section = Sections.Usage

    def test_func(self):
        return self.request.user.is_superuser

    def get_breadcrumbs(self, **kwargs):
        return build_breadcrumbs(("Usage", reverse(Sections.Usage.value)), "Edit")

    def post(self, request):
        usage_form = UsageEditForm(request.POST)
        if usage_form.is_valid():
            try:
                usage_form.save(request)
                messages.success(request, "Successfully saved usage.")
                return HttpResponseRedirect(reverse("USAGE"))
            except:  # noqa: E722
                messages.error(request, "There was an error saving usage.")
                logger.exception("Error saving usage")

        context = self.get_context_data(form=usage_form)
        return render(request, "certificat/edit-usage.html", context)

    def get(self, request):
        last_usage = Usage.objects.order_by("-created_at").first()
        usage_form = UsageEditForm(
            initial={"usage": last_usage.text if last_usage else ""}, label_suffix=""
        )
        context = self.get_context_data(form=usage_form)
        return render(request, "certificat/edit-usage.html", context)


class TermsOfServiceView(ViewBase):
    section = Sections.TOS

    def get_breadcrumbs(self, **kwargs):
        return build_breadcrumbs("Terms of Service")

    def get(self, request):
        last_tos = TermsOfService.objects.order_by("-created_at").first()
        parsed_markdown = ""
        if last_tos:
            parsed_markdown = markdown.markdown(last_tos.text)
        context = self.get_context_data(
            text=parsed_markdown,
            can_edit=request.user.is_superuser,
        )
        return render(request, "certificat/terms-of-service.html", context)


class EditTermsOfServiceView(ViewBase):
    section = Sections.TOS

    def test_func(self):
        return self.request.user.is_superuser

    def get_breadcrumbs(self, **kwargs):
        return build_breadcrumbs(
            ("Terms of Service", reverse(Sections.TOS.value)), "Edit"
        )

    def post(self, request):
        tos_form = TermsOfServiceEditForm(request.POST)
        if tos_form.is_valid():
            try:
                tos_form.save(request)
                messages.success(request, "Successfully saved terms of service.")
                return HttpResponseRedirect(reverse("TOS"))
            except:  # noqa: E722
                messages.error(request, "There was an error saving terms of service.")
                logger.exception("Error saving tos")

        context = self.get_context_data(form=tos_form)
        return render(request, "certificat/edit-tos.html", context)

    def get(self, request):
        last_tos = TermsOfService.objects.order_by("-created_at").first()
        tos_form = TermsOfServiceEditForm(
            initial={"terms_of_service": last_tos.text if last_tos else ""},
            label_suffix="",
        )
        context = self.get_context_data(form=tos_form)
        return render(request, "certificat/edit-tos.html", context)


class AccountsView(ViewBase):
    section = Sections.Accounts

    def get_context_data(self, **kwargs):
        return super().get_context_data(bindings=self.get_bindings(), **kwargs)

    def get_breadcrumbs(self, **kwargs):
        return build_breadcrumbs("Accounts")

    def get_bindings(self):
        bindings_queryset = (
            AccountBinding.objects.by_user(self.request.user)
            .filter(Q(bound_to=None) | Q(bound_to__status=AccountStatus.valid))
            .select_related("bound_to", "creator")
            .prefetch_related("group_scopes", "group_scopes__group")
            .order_by("-created_at")
        )

        filter = self.request.GET.get("filter")
        if filter:
            bindings_queryset = bindings_queryset.filter(
                Q(name__icontains=filter) | Q(note__icontains=filter)
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
    binding: AccountBinding = None

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(orders=self.get_orders(), **kwargs)

    def get_breadcrumbs(self, **kwargs):
        return build_breadcrumbs(
            ("Accounts", reverse(Sections.Accounts.value)), "Details"
        )

    def get_orders(self):
        orders = Order.objects.filter(account=self.binding.bound_to).order_by(
            "-created_at"
        )

        filter = self.request.GET.get("filter")
        if filter:
            query_filter = Q()
            for identifier in filter.split(","):
                identifier = identifier.strip()
                if identifier.startswith("/") and identifier.endswith("/"):
                    query_filter |= Q(identifiers__value__iregex=identifier[1:-1])
                else:
                    query_filter |= Q(identifiers__value__iexact=identifier.strip())

            orders = orders.filter(query_filter)

        orders_paginator = Paginator(orders, 10)
        try:
            orders_page = orders_paginator.page(self.request.GET.get("page", 1))
        except EmptyPage:
            orders_page = orders_paginator.page(1)

        return {
            "paginator": orders_paginator,
            "page": orders_page,
        }

    def dispatch(self, request, binding_id, *args, **kwargs):
        self.binding = get_object_or_404(
            AccountBinding.objects.prefetch_related("group_scopes").select_related(
                "creator",
            ),
            id=binding_id,
        )

        if not self.binding.accessible_by(request.user):
            return self.handle_no_permission()

        return super().dispatch(request, binding=self.binding, *args, **kwargs)

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
                    {"id": g.group.id, "name": unprefix_group(g.group.name)}
                    for g in binding.group_scopes.all().order_by("group__name")
                ]
            ),
            account_invalid=binding.bound_to
            and binding.bound_to.status != AccountStatus.valid,
        )

        template = "certificat/account.html"
        if not binding.bound_to:
            template = "certificat/account.activate.html"
        return render(request, template, context)


class OrderView(ViewBase):
    section = Sections.Accounts

    def get_breadcrumbs(self, **kwargs):
        order = kwargs.get("order")
        return build_breadcrumbs(
            ("Accounts", reverse(Sections.Accounts.value)),
            (
                "Account",
                reverse("account", args=[order.account.binding.id]),
            ),
            "Order Detail",
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

    def get_breadcrumbs(self, **kwargs):
        return build_breadcrumbs("Certificates")

    def get_certificates(self):
        certificates_queryset = Certificate.objects.order_by("-created_at")
        filter = self.request.GET.get("filter")
        if filter:
            query_filter = Q()
            for identifier in filter.split(","):
                identifier = identifier.strip()
                if identifier.startswith("/") and identifier.endswith("/"):
                    query_filter |= Q(
                        order__identifiers__value__iregex=identifier[1:-1]
                    )
                else:
                    query_filter |= Q(
                        order__identifiers__value__iexact=identifier.strip()
                    )

            certificates_queryset = certificates_queryset.filter(query_filter)

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

    def get_breadcrumbs(self, **kwargs):
        return build_breadcrumbs(
            ("Certificates", reverse(Sections.Certificates.value)), "Detail"
        )

    def get(self, request, cert_id):
        cert = get_object_or_404(
            Certificate.objects.select_related("order__account__binding"), pk=cert_id
        )
        context = self.get_context_data(
            cert=cert,
            user_can_access_order=cert.order.account.binding.accessible_by(
                request.user
            ),
        )

        return render(request, "certificat/certificate.html", context)


class LocalLoginView(LoginView):
    breadcrumbs = BreadCrumbs([BreadCrumb("CertifiCat", "/"), BreadCrumb("Login")])

    def get_context_data(self, **kwargs):
        return super().get_context_data(breadcrumbs=self.breadcrumbs, **kwargs)


class LocalLogoutView(LogoutView):
    http_method_names = ["get", "post", "options"]
    breadcrumbs = BreadCrumbs([BreadCrumb("CertifiCat", "/"), BreadCrumb("Logout")])

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


def handler404(request, *args, **argv):
    return render(request, "certificat/404.html", {}, status=404)


def handler500(request, *args, **argv):
    return render(request, "certificat/500.html", {}, status=500)
