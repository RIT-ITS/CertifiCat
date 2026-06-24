from dataclasses import dataclass, field
from typing import List

from certificat.settings.dynamic import (
    ApplicationSettings,
    SAMLAuthSettings,
    SAMLIdPSettings,
    SAMLSPSettings,
)
from certificat.tests.helpers import gen_user
import pytest
from certificat.auth import (
    _reconcile_idp_groups,
    _prefix_idp_groups,
    _reconcile_superuser,
)
from django.contrib.auth.models import Group, User
from certificat.auth import Saml2Backend


# @TODO: Test that SAML mappings work
@pytest.mark.django_db
def test_new_saml_user():
    saml_auth_settings = SAMLAuthSettings(
        group_attribute="memberOf",
        sp=SAMLSPSettings(
            entity_id="test.entityid", key_file="/tmp/key.pem", cert_file="/tmp/crt.pem"
        ),
        idp=SAMLIdPSettings(),
    )
    ApplicationSettings.get().authentication = saml_auth_settings

    user = User(username="acmetest", email="acmetest@acme.edu")
    backend = Saml2Backend()

    user = backend._update_user(user, {}, {})
    assert user.id is not None


@pytest.mark.django_db
def test_reconcile_groups():
    saml_auth_settings = SAMLAuthSettings(
        group_attribute="memberOf",
        sp=SAMLSPSettings(
            entity_id="test.entityid", key_file="/tmp/key.pem", cert_file="/tmp/crt.pem"
        ),
        idp=SAMLIdPSettings(),
    )
    ApplicationSettings.get().authentication = saml_auth_settings

    user = gen_user()

    # user has no groups, create all of them
    new_groups = ["group1", "group2"]
    _reconcile_idp_groups(user, {saml_auth_settings.group_attribute: new_groups})

    assert set([g.name for g in user.groups.all()]) == set(
        _prefix_idp_groups(new_groups)
    )

    # user loses access to a group, ensure it's removed
    new_groups = ["group1"]
    _reconcile_idp_groups(user, {saml_auth_settings.group_attribute: new_groups})

    assert set([g.name for g in user.groups.all()]) == set(
        _prefix_idp_groups(new_groups)
    )

    # user gets access to a non-saml group, don't remove it
    unmanaged_group, _ = Group.objects.get_or_create(name="unmanaged")
    user.groups.add(unmanaged_group)
    new_groups = ["group1", "group3"]
    _reconcile_idp_groups(user, {saml_auth_settings.group_attribute: new_groups})
    assert set([g.name for g in user.groups.all()]) == set(
        _prefix_idp_groups(new_groups)
    ) | {unmanaged_group.name}


@dataclass
class ReconcileSuperTestCase:
    admins: List[str]
    admin_groups: List[str]
    user: User
    expected_admin: bool
    initial_groups: List[str] = field(default_factory=list)
    initial_superuser: bool = False


@pytest.mark.django_db
def test_reconcile_superuser():
    """Test that an average is not a superuser unless they're a member of the admin group."""
    user = gen_user()
    case = ReconcileSuperTestCase

    test_cases = [
        # ensure basic user doesn't have access
        case(admins=[], admin_groups=[], user=user, expected_admin=False),
        # ensure user is superuser when added manually
        case(admins=[user.username], admin_groups=[], user=user, expected_admin=True),
        # ensure superuser is removed when removed from admins
        case(
            admins=[],
            admin_groups=[],
            user=user,
            expected_admin=False,
            initial_superuser=True,
        ),
        # ensure superuser is added when user is in group
        case(
            admins=[],
            admin_groups=["admin-group"],
            user=user,
            expected_admin=True,
            initial_groups=["admin-group"],
        ),
        # ensure superuser is removed when user is not in group
        case(
            admins=[],
            admin_groups=["admin-group"],
            user=user,
            expected_admin=False,
            initial_superuser=True,
            initial_groups=["nonadmin-group"],
        ),
        # ensure erroneous groups are ignored
        case(
            admins=["different-usr"],
            admin_groups=["admin-group"],
            user=user,
            expected_admin=False,
            initial_groups=["nonadmin-group", "another-nonadmin-group"],
        ),
    ]

    for idx, case in enumerate(test_cases):
        # reset user between test cases
        user.groups.clear()
        user.is_superuser = case.initial_superuser
        user.save()
        user.refresh_from_db()

        for group_name in case.initial_groups:
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)

        user = _reconcile_superuser(user, case.admins, case.admin_groups)

        assert user.is_superuser == case.expected_admin, f"Case {idx + 1} failed."
