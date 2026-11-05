"""Removes identity provider prefixes (e.g. "SAML/" or "REMOTE/") from group
names so groups map directly to the names sent by the identity provider.

If the unprefixed name is already taken, or several prefixed groups unprefix to
the same name, the groups are merged: users, permissions and account access are
moved to the surviving group and the prefixed group is deleted.
"""

import re

from django.conf import settings
from django.db import migrations

# Copied from the deprecated certificat.utils.PREFIXED_GROUP_REGEX so this
# migration keeps working after that is removed.
PREFIXED_GROUP_REGEX = re.compile(r"(?:\w+\/)?(?P<group>.+)")


def unprefixed(name: str) -> str:
    return PREFIXED_GROUP_REGEX.match(name).group("group")


def merge_group(apps, source, target):
    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    UserGroups = apps.get_model(app_label, model_name).groups.through
    AccountBindingGroupScope = apps.get_model("acme", "AccountBindingGroupScope")

    target_user_ids = set(
        UserGroups.objects.filter(group_id=target.id).values_list("user_id", flat=True)
    )
    source_user_ids = set(
        UserGroups.objects.filter(group_id=source.id).values_list("user_id", flat=True)
    )
    UserGroups.objects.bulk_create(
        [
            UserGroups(user_id=user_id, group_id=target.id)
            for user_id in source_user_ids - target_user_ids
        ]
    )

    target.permissions.add(*source.permissions.all())

    for scope in AccountBindingGroupScope.objects.filter(group_id=source.id):
        if AccountBindingGroupScope.objects.filter(
            binding_id=scope.binding_id, group_id=target.id
        ).exists():
            scope.delete()
        else:
            scope.group_id = target.id
            scope.save(update_fields=["group"])

    source.delete()


def remove_group_prefixes(apps, schema_editor):
    Group = apps.get_model("auth", "Group")

    groups = list(Group.objects.all())
    by_name = {g.name: g for g in groups if unprefixed(g.name) == g.name}

    # Shorter names first. An unprefixed name is always shorter than the
    # original, so if a prefixed group currently holds the name another group
    # will be renamed to (e.g. "a/b" vs "x/a/b"), it's renamed out of the way
    # first.
    prefixed = sorted(
        (g for g in groups if unprefixed(g.name) != g.name),
        key=lambda g: (len(g.name), g.id),
    )

    for group in prefixed:
        new_name = unprefixed(group.name)
        if new_name in by_name:
            merge_group(apps, group, by_name[new_name])
        else:
            group.name = new_name
            group.save(update_fields=["name"])
            by_name[new_name] = group


class Migration(migrations.Migration):
    dependencies = [  # noqa: RUF012
        ("acme", "0019_alter_accountbinding_owner"),
        ("auth", "0012_alter_user_first_name_max_length"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [  # noqa: RUF012
        # The original prefixes can't be recovered, so reversing leaves the
        # names as they are.
        migrations.RunPython(remove_group_prefixes, migrations.RunPython.noop),
    ]
