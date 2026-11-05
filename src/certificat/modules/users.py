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


def search_users(query: str | None = None) -> models.QuerySet[User]:
    """Searches users by username, email, first name and last name. Each
    whitespace-separated term must match at least one of those fields, so
    "jane doe" matches a user named Jane Doe."""
    queryset = User.objects.all()

    for term in (query or "").split():
        queryset = queryset.filter(
            models.Q(username__icontains=term)
            | models.Q(email__icontains=term)
            | models.Q(first_name__icontains=term)
            | models.Q(last_name__icontains=term)
        )

    return queryset.order_by("username")


def user_perms_by_category(user: User) -> dict[PermCategory, list[PermissionEntry]]:
    """Returns each manageable permission grouped by category, with the user's
    groups that grant it. Permissions are managed through groups, so
    permissions assigned directly to the user (possible in the Django admin)
    are not included."""
    granting_groups: dict[Perms, list[Group]] = {p.perm: [] for p in MANAGEABLE_PERMS}

    groups = user.groups.order_by("name").prefetch_related(
        models.Prefetch(
            "permissions",
            queryset=manageable_permissions().select_related("content_type"),
        )
    )
    for group in groups:
        for permission in group.permissions.all():
            granting_groups[Perms(permission_name(permission))].append(group)

    return by_category(
        [
            PermissionEntry(
                info,
                granted=bool(granting_groups[info.perm]),
                via_groups=granting_groups[info.perm],
            )
            for info in MANAGEABLE_PERMS
        ]
    )
