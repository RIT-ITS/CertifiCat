from certificat.tests.helpers import gen_user
import pytest
from certificat.auth import (
    _reconcile_idp_groups,
    _prefix_idp_groups,
    _reconcile_superuser,
)
from django.contrib.auth.models import Group


@pytest.mark.django_db
def test_reconcile_groups():
    from certificat.settings.saml import saml_settings

    user = gen_user()

    # user has no groups, create all of them
    new_groups = ["group1", "group2"]
    _reconcile_idp_groups(user, {saml_settings.group_attribute: new_groups})

    assert set([g.name for g in user.groups.all()]) == set(
        _prefix_idp_groups(new_groups)
    )

    # user loses access to a group, ensure it's removed
    new_groups = ["group1"]
    _reconcile_idp_groups(user, {saml_settings.group_attribute: new_groups})

    assert set([g.name for g in user.groups.all()]) == set(
        _prefix_idp_groups(new_groups)
    )

    # user gets access to a non-saml group, don't remove it
    unmanaged_group, _ = Group.objects.get_or_create(name="unmanaged")
    user.groups.add(unmanaged_group)
    new_groups = ["group1", "group3"]
    _reconcile_idp_groups(user, {saml_settings.group_attribute: new_groups})
    assert set([g.name for g in user.groups.all()]) == set(
        _prefix_idp_groups(new_groups)
    ) | {unmanaged_group.name}


@pytest.mark.django_db
def test_reconcile_superuser():
    from certificat.settings.saml import saml_settings

    user = gen_user()

    _reconcile_superuser(user, [])
    user.refresh_from_db()
    assert not user.is_superuser

    saml_settings.administrators = [user.username]

    _reconcile_superuser(user, [])
    user.refresh_from_db()
    assert user.is_superuser
