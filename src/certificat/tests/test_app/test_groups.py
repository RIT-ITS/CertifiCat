import pytest
from django.contrib.auth.models import Group, Permission
from django.test import Client
from django.urls import reverse

from certificat.modules.groups import group_perms, search_groups, set_group_perms
from certificat.modules.perms import MANAGEABLE_PERMS, PermCategory, Perms

from ..helpers import PERMS_GROUP_PREFIX, client_with_perms, gen_user


@pytest.fixture
def admin_client() -> Client:
    return client_with_perms(is_superuser=True, is_staff=True)


@pytest.fixture
def group() -> Group:
    return Group.objects.create(name="ops")


def test_every_category_has_perms():
    # Empty categories are hidden, so an unused one is probably a mistake
    assert {p.category for p in MANAGEABLE_PERMS} == set(PermCategory)


@pytest.mark.django_db
def test_requires_view_users(authenticated_web_client: Client, group: Group):
    assert authenticated_web_client.get(reverse("admin-groups")).status_code == 403
    assert (
        authenticated_web_client.get(
            reverse("admin-group", args=[group.id])
        ).status_code
        == 403
    )


@pytest.mark.django_db
def test_list_and_search(group: Group):
    other = Group.objects.create(name="auditors")
    group.permissions.add(
        Perms.VIEW_ALL_ORDERS.get_permission(),
        Perms.EDIT_TOS.get_permission(),
        Permission.objects.get(content_type__app_label="auth", codename="delete_user"),
    )
    gen_user().groups.add(group)
    gen_user().groups.add(group)

    client = client_with_perms(Perms.VIEW_USERS)
    response = client.get(reverse("admin-groups"))
    assert response.status_code == 200
    # Ignore the group client_with_perms used to grant the viewer access
    page = [
        g
        for g in response.context["groups"]["page"]
        if not g.name.startswith(PERMS_GROUP_PREFIX)
    ]
    assert page == [other, group]
    ops = page[1]
    assert ops.member_count == 2
    # Only manageable permissions are counted
    assert ops.perm_count == 2

    response = client.get(reverse("admin-groups"), {"filter": "OPS"})
    assert list(response.context["groups"]["page"]) == [group]
    assert list(search_groups("audit")) == [other]


@pytest.mark.django_db
def test_view_read_only(group: Group):
    group.permissions.add(Perms.VIEW_ALL_ORDERS.get_permission())
    client = client_with_perms(Perms.VIEW_USERS)

    response = client.get(reverse("admin-group", args=[group.id]))
    assert response.status_code == 200
    assert response.context["can_edit"] is False
    content = response.content.decode()
    assert "Update Permissions" not in content
    assert "disabled" in content

    categories = response.context["perms_by_category"]
    assert list(categories) == list(PermCategory)
    granted = {e.perm for entries in categories.values() for e in entries if e.granted}
    assert granted == {Perms.VIEW_ALL_ORDERS}

    # Viewing users isn't enough to edit groups
    response = client.post(
        reverse("admin-group", args=[group.id]), {"perms": [Perms.EDIT_TOS.value]}
    )
    assert response.status_code == 403
    assert group_perms(group) == {Perms.VIEW_ALL_ORDERS}


@pytest.mark.django_db
def test_admin_updates_permissions(admin_client: Client, group: Group):
    unmanaged = Permission.objects.get(
        content_type__app_label="auth", codename="delete_user"
    )
    group.permissions.add(Perms.VIEW_ALL_ORDERS.get_permission(), unmanaged)
    url = reverse("admin-group", args=[group.id])

    response = admin_client.get(url)
    assert response.context["can_edit"] is True
    assert "Update Permissions" in response.content.decode()

    response = admin_client.post(
        url, {"perms": [Perms.EDIT_TOS.value, Perms.EDIT_USAGE.value]}
    )
    assert response.status_code == 302
    assert group_perms(group) == {Perms.EDIT_TOS, Perms.EDIT_USAGE}
    # Permissions outside the manageable set are left alone
    assert group.permissions.filter(pk=unmanaged.pk).exists()

    # Members receive the group's permissions
    member = gen_user()
    member.groups.add(group)
    assert member.has_perm(Perms.EDIT_TOS)

    # Submitting nothing clears the manageable permissions
    response = admin_client.post(url, {})
    assert response.status_code == 302
    assert group_perms(group) == set()
    assert group.permissions.filter(pk=unmanaged.pk).exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "values", [["auth.delete_user"], [Perms.EDIT_TOS.value, "nonsense"]]
)
def test_rejects_unmanaged_permissions(admin_client: Client, group: Group, values):
    response = admin_client.post(
        reverse("admin-group", args=[group.id]), {"perms": values}
    )
    assert response.status_code == 400
    assert group.permissions.count() == 0


@pytest.mark.django_db
def test_missing_group(admin_client: Client):
    assert admin_client.get(reverse("admin-group", args=[999999])).status_code == 404


@pytest.mark.django_db
def test_set_group_perms_reports_changes(group: Group):
    added, removed = set_group_perms(group, {Perms.VIEW_USERS, Perms.EDIT_TOS})
    assert added == {Perms.VIEW_USERS, Perms.EDIT_TOS}
    assert removed == set()

    added, removed = set_group_perms(group, {Perms.VIEW_USERS})
    assert added == set()
    assert removed == {Perms.EDIT_TOS}


@pytest.mark.django_db
def test_admin_page_links_groups(group: Group):
    client = client_with_perms(Perms.VIEW_USERS)
    response = client.get(reverse("ADMIN"))
    assert reverse("admin-groups") in response.content.decode()

    # User profiles link to their groups
    member = gen_user()
    member.groups.add(group)
    response = client.get(reverse("admin-user", args=[member.id]))
    assert reverse("admin-group", args=[group.id]) in response.content.decode()
