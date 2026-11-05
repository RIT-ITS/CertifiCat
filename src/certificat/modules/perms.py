from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.auth.models import Group, Permission


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
