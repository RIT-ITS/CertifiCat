from django.contrib.auth.models import Group, User
from django.db import models

from certificat.modules.perms import (
    MANAGEABLE_PERMS,
    PermCategory,
    PermissionEntry,
    Perms,
    by_category,
    manageable_permissions,
    permission_name,
)


def can_edit_groups(user: User) -> bool:
    """Only administrators can choose which permissions a group grants."""
    return user.is_superuser


def search_groups(query: str | None = None) -> models.QuerySet[Group]:
    """Searches groups by name and annotates each with its member count and
    the number of manageable permissions it grants."""
    queryset = Group.objects.annotate(
        member_count=models.Count("user", distinct=True),
        perm_count=models.Count(
            "permissions",
            filter=models.Q(permissions__in=manageable_permissions()),
            distinct=True,
        ),
    )

    for term in (query or "").split():
        queryset = queryset.filter(name__icontains=term)

    return queryset.order_by("name")


def group_perms(group: Group) -> set[Perms]:
    """Returns the manageable permissions granted to the group."""
    permissions = group.permissions.filter(
        pk__in=manageable_permissions()
    ).select_related("content_type")
    return {Perms(permission_name(p)) for p in permissions}


def group_perms_by_category(
    group: Group,
) -> dict[PermCategory, list[PermissionEntry]]:
    """Returns each manageable permission grouped by category, marked with
    whether the group grants it."""
    granted = group_perms(group)
    return by_category(
        [PermissionEntry(info, info.perm in granted) for info in MANAGEABLE_PERMS]
    )


def set_group_perms(
    group: Group, selected: set[Perms]
) -> tuple[set[Perms], set[Perms]]:
    """Sets the group's manageable permissions to exactly `selected`. Other
    permissions on the group (for example ones assigned in the Django admin)
    are left alone. Returns the permissions that were added and removed."""
    current = group_perms(group)
    added = selected - current
    removed = current - selected

    if added:
        group.permissions.add(*(p.get_permission() for p in added))
    if removed:
        group.permissions.remove(*(p.get_permission() for p in removed))

    return added, removed
