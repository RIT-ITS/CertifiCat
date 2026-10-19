import json
import logging
from csv import Error
from dataclasses import dataclass
from typing import Any

import inject
import markdown
from acmev2.models import (
    AuthorizationStatus,
    ChallengeStatus,
    OrderStatus,
)
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.contenttypes.models import ContentType
from django.forms import Form
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic.base import ContextMixin

from certificat.modules.acme.models import (
    Account,
    AccountBinding,
    Certificate,
    CertificateRequest,
    MarkdownDisplay,
    Order,
    OrderEventType,
    TaggedEvent,
    TermsOfService,
    Usage,
)
from certificat.modules.html.forms import (
    NewBindingForm,
    TermsOfServiceEditForm,
    UsageEditForm,
)
from certificat.modules.perms import Perms
from certificat.settings.dynamic import ApplicationSettings, RemoteAuthSettings
from certificat.utils import unprefix_group

from .nav import BreadCrumb, BreadCrumbs, Sections, build_breadcrumbs

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

    def get(self, request: HttpRequest):
        recent_orders = Order.objects.by_user(request.user).recent()
        recent_certificates = Certificate.objects.recent()

        context = self.get_context_data(
            recent_orders=recent_orders, recent_certificates=recent_certificates
        )
        return render(request, "certificat/index.html", context)


class EditDynamicPageView(ViewBase):
    """Generic view used to edit the dynamic pages, such as usage or
    terms of service.

    This is an abstract class.
    """

    route_name: str = None
    display_name: str = None
    model_klass: type[MarkdownDisplay] = None
    edit_form_klass: type[Form] = None

    def test_func(self):
        return self.user_can_edit()

    def user_can_edit(self):
        content_type = ContentType.objects.get_for_model(self.model_klass)
        return self.request.user.has_perm(
            f"{content_type.app_label}.change_{content_type.model}"
        )

    def get_breadcrumbs(self, **kwargs):
        return build_breadcrumbs((self.display_name, reverse(self.route_name)), "Edit")

    def get(self, request: HttpRequest):
        last_page = self.model_klass.objects.order_by("-created_at").first()
        obj_form = self.edit_form_klass(
            initial={"text": last_page.text if last_page else ""},
            label_suffix="",
        )
        context = self.get_context_data(
            form=obj_form, display_name=self.display_name, route_name=self.route_name
        )
        return render(request, "certificat/edit-dynamic-page.html", context)

    def post(self, request: HttpRequest):
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
    """Generic view used to display dynamic pages.

    This is an abstract class.
    """

    edit_route_name: str = None
    display_name: str = None
    model_klass: type[MarkdownDisplay] = None

    def user_can_edit(self):
        content_type = ContentType.objects.get_for_model(self.model_klass)
        return self.request.user.has_perm(
            f"{content_type.app_label}.change_{content_type.model}"
        )

    def get_breadcrumbs(self, **kwargs):
        return build_breadcrumbs(self.display_name)

    def get(self, request: HttpRequest):
        last_page = self.model_klass.objects.order_by("-created_at").first()
        parsed_markdown = ""
        if last_page:
            parsed_markdown = markdown.markdown(last_page.text)

        context = self.get_context_data(
            text=parsed_markdown,
            display_name=self.display_name,
            edit_route_name=self.edit_route_name,
            can_edit=self.user_can_edit(),
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
        bindings_paginator, bindings_page = (
            AccountBinding.objects.by_user(self.request.user)
            .active(self.request.GET.get("filter"))
            .paginated(self.request.GET.get("page", 1))
        )

        return {
            "paginator": bindings_paginator,
            "page": bindings_page,
        }

    def get(self, request: HttpRequest):
        new_binding_form = NewBindingForm(request.user, label_suffix="")
        context = self.get_context_data(new_binding_form=new_binding_form)

        return render(request, "certificat/accounts.html", context)

    def post(self, request: HttpRequest):
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


class AccountFinalizerController:
    DEFAULT_FINALIZER = "https://github.com/RIT-ITS/CertifiCat/finalizer/default"
    DEFAULT_FINALIZER_VALUES = {  # noqa: RUF012
        "name": "Default",
        "description": "This is the default finalizer configured for the CertifiCat instance.",
    }
    settings = inject.attr(ApplicationSettings)

    def __init__(self, request: HttpRequest, account: Account):
        self.request = request
        self.account = account

    def should_display_finalizer(self):
        user_has_access = self.request.user.is_superuser
        multiple_finalizers = len(self.settings.alternative_finalizers) > 0
        non_default_finalizer_selected = self.account.finalizer is not None

        return (
            user_has_access and multiple_finalizers
        ) or non_default_finalizer_selected

    def editable(self):
        return self.request.user.is_superuser

    def selected_finalizer(self) -> str:
        return self.account.finalizer or ""

    def finalizers_json(self) -> str:
        fin = {self.DEFAULT_FINALIZER: self.DEFAULT_FINALIZER_VALUES}

        for alt in self.settings.alternative_finalizers:
            fin[alt.id] = {"name": alt.name, "description": alt.description}

        return json.dumps(fin)


class AccountViewContext:
    def __init__(self, request: HttpRequest, binding: AccountBinding, initial: dict):
        self.request = request
        self.binding = binding
        self.initial = initial

    def show_pre_authorized_identifiers(self):
        if not self.binding.bound_to:
            return False

        return len(
            self.binding.bound_to.preauthorized_identifiers.all()
        ) > 0 or self.request.user.has_perm(Perms.EDIT_PREAUTHS)

    def as_dict(self) -> dict:
        editable = self.binding.editable_by(self.request.user)

        return self.initial | {
            "access_group_json": json.dumps(
                [
                    {"id": g.group.id, "name": unprefix_group(g.group.name)}
                    for g in sorted(
                        self.binding.group_scopes.all(), key=lambda gs: gs.group.name
                    )
                ]
            ),
            "account_invalid": self.binding.account_invalid(),
            "binding_event": TaggedEvent.objects.bound_to_event(self.binding),
            "show_pre_authorized_identifiers": self.show_pre_authorized_identifiers(),
            "can_edit": editable,
            "can_edit_preauthorizations": editable
            and self.request.user.has_perm(Perms.EDIT_PREAUTHS),
            "finalizer_controller": AccountFinalizerController(
                self.request, self.binding.bound_to
            ),
            "pre_authorized_identifiers_json": json.dumps(
                [
                    {"name": r.identifier_value}
                    for r in self.binding.bound_to.preauthorized_identifiers.all()
                ]
            )
            if self.binding.bound_to
            else [],
        }


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
        orders = Order.objects.by_account(self.binding.bound_to).search(
            self.request.GET.get("filter")
        )
        orders_paginator, orders_page = orders.paginated(
            self.request.GET.get("page", 1)
        )

        return {
            "paginator": orders_paginator,
            "page": orders_page,
        }

    def dispatch(
        self, request: HttpRequest, binding_id: int, tab="details", *args, **kwargs
    ):
        self.binding = get_object_or_404(
            AccountBinding.objects.prefetch_related(
                "group_scopes", "group_scopes__group"
            ).select_related(
                "creator",
            ),
            id=binding_id,
        )

        if not self.binding.accessible_by(request.user):
            return self.handle_no_permission()

        kwargs.update({"tab": tab, "binding": self.binding})
        return super().dispatch(request, *args, **kwargs)

    def post(self, request: HttpRequest, binding: AccountBinding, tab: str):
        if not binding.editable_by(request.user):
            return HttpResponse(status=403)

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

    def get(self, request, binding: AccountBinding, tab: str, *args, **kwargs):
        initial_context = self.get_context_data(
            binding=binding,
            tab=tab,
        )

        if binding.bound_to:
            template = "certificat/account.html"
        else:
            template = "certificat/account.activate.html"

        return render(
            request,
            template,
            AccountViewContext(request, binding, initial=initial_context).as_dict(),
        )


@dataclass
class OrderStage:
    name: str
    completed: str
    description: str = None
    error_help: str = None
    current: bool = False

    def upcoming(self):
        return not self.completed and not self.current


class OrderStatusController:
    request: HttpRequest
    order: Order
    messages: list[str]

    def __init__(self, request: HttpRequest, order: Order):
        self.request = request
        self.order = order
        self.messages = []

    def stages(self) -> list[OrderStage]:
        order_stages: list[OrderStage] = [
            OrderStage(
                "Order created",
                self.order_created(),
            ),
            OrderStage(
                "Authorizations ready",
                self.authorizations_not_pending(),
                "The server is waiting for the client to indicate challenges can be validated.",
                "The server never received a message from the client to validate challenges.",
            ),
            OrderStage(
                "Authorizations processing",
                self.authorizations_satisfied(),
                "The server is executing challenges to authorize identifiers.",
                "One or more client challenge was unable to be validated.",
            ),
            OrderStage(
                "Order ready",
                self.csr_submitted(),
                "All identifiers have been authorized, the server is waiting for the client to submit a CSR.",
                "The client did not finalize the order.",  # This should never be hit
            ),
            OrderStage(
                "Upstream order processing",
                self.certificate_ready(),
                "The server is waiting on the upstream finalizer for a certificate.",
                "There was an error with the upstream finalizer. Please check the finalization section for more detail.",
            ),
            OrderStage(
                "Certificate ready",
                self.certificate_ready(),
                "The certificate was successfully generated by the upstream finalizer.",
            ),
        ]

        for idx, stage in enumerate(order_stages):
            if idx == len(order_stages) - 1:
                stage.current = True

            if not stage.completed:
                stage.current = True
                break

        return order_stages

    def order_invalid(self):
        return self.order.status == OrderStatus.invalid

    def order_created(self):
        return True

    def authorizations_not_pending(self) -> bool:
        for auth in self.order.authorizations.all():
            if auth.status == AuthorizationStatus.valid:
                return True

            for chall in auth.challenges.all():
                if chall.status != ChallengeStatus.pending:
                    return True

        return False

    def authorizations_satisfied(self) -> bool:
        for auth in self.order.authorizations.all():
            if auth.status != AuthorizationStatus.valid:
                return False

        return True

    def csr_submitted(self) -> bool:
        return CertificateRequest.objects.filter(order=self.order).exists()

    def certificate_ready(self) -> bool:
        return self.order.status == OrderStatus.valid


class OrderView(ViewBase):
    section = Sections.Accounts

    def get_breadcrumbs(self, **kwargs):
        order = kwargs.get("order")
        breadcrumbs = [
            ("Accounts", reverse(Sections.Accounts.value)),
        ]
        if order.account.binding.accessible_by(self.request.user):
            breadcrumbs.append(
                (
                    "Account",
                    reverse("account", args=[order.account.binding.id]),
                )
            )
        breadcrumbs.append("Order Detail")
        return build_breadcrumbs(*breadcrumbs)

    def get(self, request: HttpRequest, order_id):
        order: Order = get_object_or_404(
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
        if not order.accessible_by(request.user):
            return self.handle_no_permission()

        creation_event = order.events.filter(event_type=OrderEventType.CREATED).first()
        context = self.get_context_data(
            order=order,
            status_controller=OrderStatusController(request, order),
            creation_event=creation_event,
        )
        return render(request, "certificat/order.html", context)


class OrdersView(ViewBase):
    section = Sections.Orders

    def get_context_data(self, **kwargs):
        return super().get_context_data(orders=self.get_orders(), **kwargs)

    def get_breadcrumbs(self, **kwargs):
        return build_breadcrumbs("Orders")

    def get_orders(self):
        orders_queryset = Order.objects.by_user(self.request.user).search(
            self.request.GET.get("filter")
        )
        orders_paginator, orders_page = orders_queryset.paginated(
            self.request.GET.get("page", 1), per_page=20
        )

        return {
            "paginator": orders_paginator,
            "page": orders_page,
        }

    def get(self, request):
        context = self.get_context_data()

        return render(request, "certificat/orders.html", context)


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
    http_method_names = ["get", "post", "options"]  # noqa: RUF012

    def get_context_data(self, **kwargs):
        breadcrumbs = BreadCrumbs(
            [
                BreadCrumb("CertifiCat", reverse(Sections.Dashboard.value)),
                BreadCrumb("Logout"),
            ]
        )
        return super().get_context_data(breadcrumbs=breadcrumbs, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs):
        from django.contrib.auth import logout as auth_logout

        auth_logout(request)
        context = self.get_context_data()
        return render(request, "certificat/logout.html", context=context)


def acs_failure(request: HttpRequest, exception: Error, status, **kwargs):
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


def remote_login_redirect(request: HttpRequest, *args, **kwargs):
    app_settings = inject.instance(ApplicationSettings)

    if app_settings.authentication.type != "remote":
        raise Exception("What are you doing?")  # noqa: TRY002

    redirect_target = request.GET.get("next", app_settings.web_ui_mountpoint)
    remote_auth_settings: RemoteAuthSettings = app_settings.authentication

    return redirect(
        remote_auth_settings.redirect_template.format(redirect=redirect_target)
    )


def handler404(request: HttpRequest, *args, **argv):
    return render(request, "certificat/404.html", {}, status=404)


def handler500(request: HttpRequest, *args, **argv):
    return render(request, "certificat/500.html", {}, status=500)
