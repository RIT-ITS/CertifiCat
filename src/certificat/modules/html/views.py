import json
from typing import Any
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse
from django.views.generic.base import ContextMixin
from django.views import View
from django.shortcuts import get_object_or_404, redirect, render
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
from certificat.settings.dynamic import ApplicationSettings, RemoteAuthSettings
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
            .prefetch_related("identifiers")
            .distinct()[:10]
        )
        recent_certificates = Certificate.objects.all().order_by("-created_at")[:10]

        context = self.get_context_data(
            recent_orders=recent_orders, recent_certificates=recent_certificates
        )
        return render(request, "certificat/index.html", context)


class EditDynamicPageView(ViewBase):
    route_name: str = None
    display_name: str = None
    model_klass: type = None
    edit_form_klass: type = None

    def test_func(self):
        return self.request.user.is_superuser

    def get_breadcrumbs(self, **kwargs):
        return build_breadcrumbs((self.display_name, reverse(self.route_name)), "Edit")

    def get(self, request):
        last_page = self.model_klass.objects.order_by("-created_at").first()
        obj_form = self.edit_form_klass(
            initial={"text": last_page.text if last_page else ""},
            label_suffix="",
        )
        context = self.get_context_data(
            form=obj_form, display_name=self.display_name, route_name=self.route_name
        )
        return render(request, "certificat/edit-dynamic-page.html", context)

    def post(self, request):
        obj_form = self.edit_form_klass(request.POST)
        if obj_form.is_valid():
            try:
                obj_form.save(request)
                messages.success(request, "Successfully saved edits.")
                return HttpResponseRedirect(reverse(self.route_name))
            except:  # noqa: E722
                messages.error(request, "There was an error saving your edits.")
                logger.exception("Error saving edits")

        context = self.get_context_data(
            form=obj_form, display_name=self.display_name, route_name=self.route_name
        )
        return render(request, "certificat/edit-dynamic-page.html", context)


class DynamicPageView(ViewBase):
    edit_route_name: str = None
    display_name: str = None
    model_klass: type = None

    def get_breadcrumbs(self, **kwargs):
        return build_breadcrumbs(self.display_name)

    def get(self, request):
        last_page = self.model_klass.objects.order_by("-created_at").first()
        parsed_markdown = ""
        if last_page:
            parsed_markdown = markdown.markdown(last_page.text)

        context = self.get_context_data(
            text=parsed_markdown,
            display_name=self.display_name,
            edit_route_name=self.edit_route_name,
            can_edit=request.user.is_superuser,
        )
        return render(request, "certificat/dynamic-page.html", context)


class UsageView(DynamicPageView):
    section = Sections.Usage
    edit_route_name = "edit-usage"
    display_name = "Usage"
    model_klass = Usage


class EditUsageView(EditDynamicPageView):
    section = Sections.Usage
    route_name = "USAGE"
    display_name = "Usage"
    model_klass = Usage
    edit_form_klass = UsageEditForm


class TermsOfServiceView(DynamicPageView):
    section = Sections.TOS
    edit_route_name = "edit-tos"
    display_name = "Terms of Service"
    model_klass = TermsOfService


class EditTermsOfServiceView(EditDynamicPageView):
    route_name = "TOS"
    display_name = "Terms of Service"
    model_klass = TermsOfService
    edit_form_klass = TermsOfServiceEditForm


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
        ).distinct()

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


class LocalLoginView(LoginView):
    def get_context_data(self, **kwargs):
        breadcrumbs = BreadCrumbs(
            [
                BreadCrumb("CertifiCat", reverse(Sections.Dashboard.value)),
                BreadCrumb("Login"),
            ]
        )
        return super().get_context_data(breadcrumbs=breadcrumbs, **kwargs)


class LocalLogoutView(LogoutView):
    http_method_names = ["get", "post", "options"]

    def get_context_data(self, **kwargs):
        breadcrumbs = BreadCrumbs(
            [
                BreadCrumb("CertifiCat", reverse(Sections.Dashboard.value)),
                BreadCrumb("Logout"),
            ]
        )
        return super().get_context_data(breadcrumbs=breadcrumbs, **kwargs)

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
            "saml_settings": inject.instance(ApplicationSettings).authentication,
        },
    )


def remote_login_redirect(request, *args, **kwargs):
    app_settings = inject.instance(ApplicationSettings)

    if app_settings.authentication.type != "remote":
        raise Exception("What are you doing?")

    redirect_target = request.GET.get("next", app_settings.web_ui_mountpoint)
    remote_auth_settings: RemoteAuthSettings = app_settings.authentication

    return redirect(
        remote_auth_settings.redirect_template.format(redirect=redirect_target)
    )


def handler404(request, *args, **argv):
    return render(request, "certificat/404.html", {}, status=404)


def handler500(request, *args, **argv):
    return render(request, "certificat/500.html", {}, status=500)
