import json
import logging
from typing import Any

import inject
from django.contrib import messages
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from certificat.modules.acme.models import (
    Account,
    AccountBinding,
    Order,
    TaggedEvent,
)
from certificat.modules.html.forms import (
    NewBindingForm,
)
from certificat.modules.perms import (
    AccountGateContext,
    Gates,
    PermissionGate,
    require_gate,
)
from certificat.settings.dynamic import ApplicationSettings

from ..nav import Sections, build_breadcrumbs
from .base import ViewBase

logger = logging.getLogger(__name__)


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

    def __init__(self, account: Account, can_edit: bool):
        self.account = account
        self.can_edit = can_edit

    def should_display_finalizer(self):
        multiple_finalizers = len(self.settings.alternative_finalizers) > 0
        non_default_finalizer_selected = self.account.finalizer is not None

        return (self.can_edit and multiple_finalizers) or non_default_finalizer_selected

    def editable(self):
        return self.can_edit

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
        ) > 0 or PermissionGate.evaluate(self.request.user, Gates.EDIT_PREAUTHS)

    def as_dict(self) -> dict:
        editable = PermissionGate.evaluate(
            self.request.user, Gates.EDIT_ACCOUNT, AccountGateContext(self.binding)
        )
        transferrable = PermissionGate.evaluate(
            self.request.user, Gates.TRANSFERRABLE_BY, AccountGateContext(self.binding)
        )
        show_preauths = self.show_pre_authorized_identifiers()

        return self.initial | {
            "access_group_json": json.dumps(
                [
                    {"id": g.group.id, "name": g.group.name}
                    for g in sorted(
                        self.binding.group_scopes.all(), key=lambda gs: gs.group.name
                    )
                ]
            ),
            "account_invalid": self.binding.account_invalid(),
            "binding_event": TaggedEvent.objects.bound_to_event(self.binding),
            "show_pre_authorized_identifiers": show_preauths,
            "can_edit": editable,
            "can_edit_preauthorizations": editable and show_preauths,
            "can_transfer": transferrable,
            "finalizer_controller": AccountFinalizerController(
                self.binding.bound_to, editable
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

        kwargs.update({"tab": tab, "binding": self.binding})
        return super().dispatch(request, *args, **kwargs)

    def fetch_account_gate_context(self, *args, **kwargs):
        return AccountGateContext(self.binding)

    @require_gate(Gates.VIEW_ACCOUNT, get_context=fetch_account_gate_context)
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

    @require_gate(Gates.EDIT_ACCOUNT, get_context=fetch_account_gate_context)
    def post(self, request: HttpRequest, binding: AccountBinding, tab: str):
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
