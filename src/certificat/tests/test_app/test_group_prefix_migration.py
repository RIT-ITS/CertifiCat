from importlib import import_module

import pytest
from django.apps import apps
from django.contrib.auth.models import Group

from certificat.modules.acme import models as db
from certificat.modules.perms import Perms

from ..helpers import gen_user

migration = import_module(
    "certificat.modules.acme.migrations.0020_remove_group_prefixes"
)


def run_migration():
    migration.remove_group_prefixes(apps, None)


def names() -> set[str]:
    return set(Group.objects.values_list("name", flat=True))


@pytest.mark.django_db
def test_renames_prefixed_groups():
    user = gen_user()
    saml = Group.objects.create(name="SAML/admins")
    remote = Group.objects.create(name="REMOTE/ops")
    plain = Group.objects.create(name="plain")
    spaced = Group.objects.create(name="Domain Admins/x")
    user.groups.add(saml, remote, plain)

    run_migration()

    assert names() == {"admins", "ops", "plain", "Domain Admins/x"}
    # Renamed in place, so ids, members and permissions are kept
    saml.refresh_from_db()
    assert saml.name == "admins"
    assert set(user.groups.values_list("name", flat=True)) == {
        "admins",
        "ops",
        "plain",
    }
    spaced.refresh_from_db()
    assert spaced.name == "Domain Admins/x"


@pytest.mark.django_db
def test_merges_into_existing_group():
    existing = Group.objects.create(name="admins")
    prefixed = Group.objects.create(name="SAML/admins")
    existing.permissions.add(Perms.VIEW_ALL_ORDERS.get_permission())
    prefixed.permissions.add(Perms.VIEW_ALL_ACCOUNTS.get_permission())

    in_both, only_prefixed, only_existing = gen_user(), gen_user(), gen_user()
    in_both.groups.add(existing, prefixed)
    only_prefixed.groups.add(prefixed)
    only_existing.groups.add(existing)

    shared_binding = db.AccountBinding.generate(in_both, "shared", "note")
    db.AccountBindingGroupScope.objects.create(binding=shared_binding, group=existing)
    db.AccountBindingGroupScope.objects.create(binding=shared_binding, group=prefixed)
    prefixed_binding = db.AccountBinding.generate(in_both, "prefixed", "note")
    db.AccountBindingGroupScope.objects.create(binding=prefixed_binding, group=prefixed)

    run_migration()

    assert names() == {"admins"}
    assert not Group.objects.filter(pk=prefixed.pk).exists()
    assert set(existing.user_set.all()) == {in_both, only_prefixed, only_existing}
    assert set(existing.permissions.values_list("codename", flat=True)) == {
        Perms.VIEW_ALL_ORDERS.codename,
        Perms.VIEW_ALL_ACCOUNTS.codename,
    }
    assert [s.group for s in shared_binding.group_scopes.all()] == [existing]
    assert [s.group for s in prefixed_binding.group_scopes.all()] == [existing]


@pytest.mark.django_db
def test_merges_prefixed_groups_with_same_name():
    saml = Group.objects.create(name="SAML/team")
    remote = Group.objects.create(name="REMOTE/team")
    user_a, user_b = gen_user(), gen_user()
    user_a.groups.add(saml)
    user_b.groups.add(remote)

    run_migration()

    assert names() == {"team"}
    team = Group.objects.get(name="team")
    assert set(team.user_set.all()) == {user_a, user_b}


@pytest.mark.django_db
def test_renamed_group_frees_name_for_another():
    # "x/a/b" unprefixes to "a/b", which is held by a group that is itself
    # renamed to "b".
    deep = Group.objects.create(name="x/a/b")
    shallow = Group.objects.create(name="a/b")

    run_migration()

    deep.refresh_from_db()
    shallow.refresh_from_db()
    assert shallow.name == "b"
    assert deep.name == "a/b"


@pytest.mark.django_db
def test_idempotent():
    Group.objects.create(name="SAML/admins")
    run_migration()
    run_migration()
    assert names() == {"admins"}
