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
from django.contrib.auth.models import Group


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


@pytest.mark.django_db
def test_reconcile_superuser():
    """Test that an average is not a superuser unless they're a member of the admin group."""
    user = gen_user()

    _reconcile_superuser(user, [])
    user.refresh_from_db()
    assert not user.is_superuser

    _reconcile_superuser(user, [user.username, "dummy-user"])
    user.refresh_from_db()
    assert user.is_superuser

    _reconcile_superuser(user, ["dummy-user"])
    user.refresh_from_db()
    assert not user.is_superuser
