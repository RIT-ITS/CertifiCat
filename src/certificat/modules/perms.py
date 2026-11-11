import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from functools import wraps
from typing import TYPE_CHECKING

from django.http import HttpRequest, HttpResponse

from certificat.modules.acme import models as db

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from django.contrib.auth.models import Group, Permission, User


class Perms(StrEnum):
    VIEW_ALL_ORDERS = "acme.view_order"
    VIEW_ALL_ACCOUNTS = "acme.view_account"
    CHANGE_ALL_ACCOUNTS = "acme.change_account"
    EDIT_PREAUTHS = "acme.change_preauthorizedaccountidentifier"
    EDIT_USAGE = "acme.change_usage"
    EDIT_TOS = "acme.change_termsofservice"
    VIEW_USERS = "auth.view_user"

    @property
    def app_label(self) -> str:
        return self.value.split(".", 1)[0]

    @property
    def codename(self) -> str:
        return self.value.split(".", 1)[1]

    def get_permission(self):
        # Imported lazily; this module is imported while models are loading.
        from django.contrib.auth.models import Permission

        return Permission.objects.get(
            content_type__app_label=self.app_label, codename=self.codename
        )


class Gates(StrEnum):
    EDIT_ACCOUNT = "edit_account"
    VIEW_ACCOUNT = "view_account"
    VIEW_ORDER = "view_order"
    VIEW_GROUPS = "view_groups"
    EDIT_GROUPS = "edit_groups"
    VIEW_USERS = "view_users"
    EDIT_PREAUTHS = "edit_preauths"
    TRANSFERRABLE_BY = "transferrable_by"
    EDIT_USAGE = "edit_usage"
    EDIT_TOS = "edit_tos"
    CAN_ACCESS_MANAGEMENT = "access_management"


class PermissionDeniedError(Exception):
    pass


class GateContext:
    pass


@dataclass
class AccountGateContext(GateContext):
    binding: db.AccountBinding


@dataclass
class OrderGateContext(GateContext):
    order: db.Order


class UserPermissionGate:
    def __init__(self, user: User):
        self.user = user

    def evaluate(self, action: Gates, ctx: GateContext | None = None) -> bool:
        return PermissionGate.evaluate(self.user, action, ctx)


class PermissionGate:
    """
    This routes permission gates to evaluators so permission evaluation can be centralized.
    """

    @staticmethod
    def throw_if_fails(user: User, action: Gates, ctx: GateContext | None = None):
        if not user or not user.is_authenticated:
            raise PermissionDeniedError("User was not authenticated")

        if not PermissionGate.evaluate(user, action, ctx):
            raise PermissionDeniedError(f"Permission denied for gate '{action.value}'")

    @staticmethod
    def evaluate(user: User, action: Gates, ctx: GateContext | None = None) -> bool:
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        passed = False

        match action:
            case Gates.VIEW_ACCOUNT:
                passed = PermissionGate.can_view_account(user, ctx)
            case Gates.VIEW_ORDER:
                passed = PermissionGate.can_view_order(user, ctx)
            case Gates.VIEW_USERS | Gates.VIEW_GROUPS:
                passed = user.has_perm(Perms.VIEW_USERS)
            case Gates.EDIT_GROUPS:
                passed = user.is_superuser
            case Gates.EDIT_ACCOUNT:
                passed = PermissionGate.can_edit_account(user, ctx)
            case Gates.TRANSFERRABLE_BY:
                passed = PermissionGate.can_transfer_account(user, ctx)
            case Gates.EDIT_PREAUTHS:
                passed = PermissionGate.can_edit_preauthorizations(user)
            case Gates.EDIT_USAGE:
                passed = user.has_perm(Perms.EDIT_USAGE)
            case Gates.EDIT_TOS:
                passed = user.has_perm(Perms.EDIT_TOS)
            case Gates.CAN_ACCESS_MANAGEMENT:
                passed = (
                    user.is_superuser
                    or user.is_staff
                    or any(
                        user.has_perm(p)
                        for p in (
                            Perms.VIEW_USERS,
                            Perms.EDIT_TOS,
                            Perms.EDIT_USAGE,
                        )
                    )
                )
            case _:
                raise Exception(f"Unhandled permission gate {action.value}")  # noqa: TRY002

        if not passed:
            logger.info(
                f"User {user.username} failed permission gate. ctx={ctx}, action='{action.value}'"
            )
            return False

        return True

    @staticmethod
    def can_edit_preauthorizations(user: User):
        return user.has_perm(Perms.EDIT_PREAUTHS)

    @staticmethod
    def can_view_account(user: User, ctx: AccountGateContext) -> bool:
        return ctx.binding.accessible_by(user)

    @staticmethod
    def can_view_order(user: User, ctx: OrderGateContext) -> bool:
        return ctx.order.accessible_by(user)

    @staticmethod
    def can_edit_account(user: User, ctx: AccountGateContext) -> bool:
        return ctx.binding.editable_by(user)

    @staticmethod
    def can_transfer_account(user: User, ctx: AccountGateContext) -> bool:
        return ctx.binding.transferable_by(user)


def normalize_gate_error(view_func):
    @wraps(view_func)
    def _wrapped_view(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except PermissionDeniedError:
            return HttpResponse(status=403)

    return _wrapped_view


def require_gate(
    action: Gates, get_context: Callable[[HttpRequest], GateContext] | None = None
):
    """
    Decorator that forces a view through the PermissionGate before executing.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(*args, **kwargs):
            # request will be the first or second parameter depending on if this is a
            # class or function-based view
            request = args[0] if isinstance(args[0], HttpRequest) else args[1]
            context = get_context(*args, **kwargs) if get_context else None
            PermissionGate.throw_if_fails(request.user, action, context)

            return view_func(*args, **kwargs)

        return _wrapped_view

    return decorator


class PermCategory(StrEnum):
    USERS = "Users"
    ACCOUNTS_ORDERS = "Accounts & Orders"
    DOCUMENTATION = "Documentation"


@dataclass(frozen=True)
class PermDescription:
    perm: Perms
    name: str
    description: str
    category: PermCategory


# The subset of Django permissions that are used throughout
# the application, in display order.
MANAGEABLE_PERMS: tuple[PermDescription, ...] = (
    PermDescription(
        Perms.VIEW_USERS,
        "View users",
        "View the user and group lists, user profiles and group permissions.",
        PermCategory.USERS,
    ),
    PermDescription(
        Perms.VIEW_ALL_ACCOUNTS,
        "View all accounts",
        "View every ACME account binding, regardless of owner or group access.",
        PermCategory.ACCOUNTS_ORDERS,
    ),
    PermDescription(
        Perms.CHANGE_ALL_ACCOUNTS,
        "Manage all accounts",
        "Edit, revoke and transfer ownership of any ACME account binding.",
        PermCategory.ACCOUNTS_ORDERS,
    ),
    PermDescription(
        Perms.VIEW_ALL_ORDERS,
        "View all orders",
        "View every ACME order, regardless of account access.",
        PermCategory.ACCOUNTS_ORDERS,
    ),
    PermDescription(
        Perms.EDIT_PREAUTHS,
        "Manage pre-authorizations",
        "Add and remove pre-authorized identifiers on accounts the user can edit.",
        PermCategory.ACCOUNTS_ORDERS,
    ),
    PermDescription(
        Perms.EDIT_TOS,
        "Edit terms of service",
        "Edit the content of the terms of service page.",
        PermCategory.DOCUMENTATION,
    ),
    PermDescription(
        Perms.EDIT_USAGE,
        "Edit usage page",
        "Edit the content of the usage page.",
        PermCategory.DOCUMENTATION,
    ),
)

MANAGEABLE_PERMS_BY_VALUE: dict[str, PermDescription] = {
    p.perm.value: p for p in MANAGEABLE_PERMS
}


@dataclass
class PermissionEntry:
    """A manageable permission as shown on the user and group pages."""

    info: PermDescription
    granted: bool
    # Groups that grant the permission, only filled in on the user page
    via_groups: list["Group"] = field(default_factory=list)

    @property
    def perm(self) -> Perms:
        return self.info.perm

    @property
    def name(self) -> str:
        return self.info.name

    @property
    def description(self) -> str:
        return self.info.description

    @property
    def category(self) -> PermCategory:
        return self.info.category


def by_category(
    entries: list[PermissionEntry],
) -> dict[PermCategory, list[PermissionEntry]]:
    """Groups permission entries by category, in display order."""
    grouped: dict[PermCategory, list[PermissionEntry]] = {c: [] for c in PermCategory}
    for entry in entries:
        grouped[entry.category].append(entry)
    return {c: e for c, e in grouped.items() if e}


def permission_name(permission: "Permission") -> str:
    """Returns the "app_label.codename" name of a Django Permission, the form
    used by Perms and user.has_perm."""
    return f"{permission.content_type.app_label}.{permission.codename}"


def manageable_permissions():
    """Returns a queryset of the Django Permission rows for MANAGEABLE_PERMS."""
    from django.contrib.auth.models import Permission
    from django.db.models import Q

    query = Q()
    for p in MANAGEABLE_PERMS:
        query |= Q(content_type__app_label=p.perm.app_label, codename=p.perm.codename)
    return Permission.objects.filter(query)
