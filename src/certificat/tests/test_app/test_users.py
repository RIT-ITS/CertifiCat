import pytest
from django.contrib.auth.models import Group
from django.test import Client
from django.urls import reverse

from certificat.modules.perms import MANAGEABLE_PERMS, PermCategory, Perms
from certificat.modules.users import search_users

from ..helpers import client_with_perms, gen_user


@pytest.mark.django_db
def test_manageable_perms_exist():
    # Every manageable permission must map to a real Django permission.
    for description in MANAGEABLE_PERMS:
        assert description.perm.get_permission()


@pytest.mark.django_db
def test_anonymous_redirected(web_client: Client):
    assert web_client.get(reverse("admin-users")).status_code == 302


@pytest.mark.django_db
def test_users_requires_view_perm(authenticated_web_client: Client):
    other = gen_user()
    assert authenticated_web_client.get(reverse("admin-users")).status_code == 403
    assert (
        authenticated_web_client.get(reverse("admin-user", args=[other.id])).status_code
        == 403
    )


@pytest.mark.django_db
def test_list_and_search_users():
    client = client_with_perms(Perms.VIEW_USERS)
    jane = gen_user(first_name="Jane", last_name="Doe", email="jdoe@example.edu")
    other = gen_user(first_name="Other", last_name="Person")

    response = client.get(reverse("admin-users"))
    assert response.status_code == 200
    page_users = list(response.context["users"]["page"])
    assert jane in page_users
    assert other in page_users

    response = client.get(reverse("admin-users"), {"filter": "jane doe"})
    assert list(response.context["users"]["page"]) == [jane]


@pytest.mark.django_db
def test_search_users_fields():
    u = gen_user(username="zz-unique", email="findme@example.edu", last_name="Qux")
    assert list(search_users("zz-uniq")) == [u]
    assert list(search_users("FINDME@")) == [u]
    assert list(search_users("qux")) == [u]
    assert u in search_users("")


def flatten(perms_by_category):
    return {e.perm: e for entries in perms_by_category.values() for e in entries}


@pytest.mark.django_db
def test_profile_shows_permissions_by_group():
    client = client_with_perms(Perms.VIEW_USERS)
    other = gen_user()
    admins = Group.objects.create(name="admins")
    auditors = Group.objects.create(name="auditors")
    admins.permissions.add(
        Perms.VIEW_ALL_ACCOUNTS.get_permission(), Perms.EDIT_TOS.get_permission()
    )
    auditors.permissions.add(Perms.VIEW_ALL_ACCOUNTS.get_permission())
    other.groups.add(admins, auditors)

    response = client.get(reverse("admin-user", args=[other.id]))
    assert response.status_code == 200

    categories = response.context["perms_by_category"]
    assert list(categories) == list(PermCategory)
    entries = flatten(categories)
    assert entries[Perms.VIEW_ALL_ACCOUNTS].via_groups == [admins, auditors]
    assert entries[Perms.EDIT_TOS].via_groups == [admins]
    assert not entries[Perms.VIEW_ALL_ORDERS].granted

    content = response.content.decode()
    # Test that links to the groups providing the perms exists
    assert reverse("admin-group", args=[admins.id]) in content
    assert reverse("admin-group", args=[auditors.id]) in content


@pytest.mark.django_db
def test_profile_does_not_accept_grants():
    client = client_with_perms(Perms.VIEW_USERS, is_superuser=True)
    other = gen_user()

    response = client.post(
        reverse("admin-user", args=[other.id]), {"grant": Perms.VIEW_ALL_ORDERS.value}
    )
    assert response.status_code == 405
    assert other.user_permissions.count() == 0


@pytest.mark.django_db
def test_view_profile_missing_user():
    client = client_with_perms(Perms.VIEW_USERS)
    assert client.get(reverse("admin-user", args=[999999])).status_code == 404


@pytest.mark.django_db
def test_profile_ignores_direct_grants():
    # Permissions are managed through groups, so a permission assigned
    # directly to the user (possible in the Django admin) isn't shown.
    client = client_with_perms(Perms.VIEW_USERS)
    other = gen_user()
    other.user_permissions.add(Perms.VIEW_ALL_ORDERS.get_permission())

    response = client.get(reverse("admin-user", args=[other.id]))
    entry = flatten(response.context["perms_by_category"])[Perms.VIEW_ALL_ORDERS]
    assert not entry.granted
    assert entry.via_groups == []


@pytest.mark.django_db
@pytest.mark.parametrize("page", ["abc", "999"])
def test_list_tolerates_bad_page_numbers(page):
    client = client_with_perms(Perms.VIEW_USERS)
    response = client.get(reverse("admin-users"), {"page": page})
    assert response.status_code == 200
    assert client.test_user in list(response.context["users"]["page"])
