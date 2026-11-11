import time

import pytest
from acmev2.models import AccountStatus, OrderStatus
from django.contrib.auth.models import AnonymousUser, Group, Permission
from django.test import Client, RequestFactory
from django.urls import reverse
from django.utils import timezone

from certificat.modules import management
from certificat.modules.acme import models as db
from certificat.modules.html.nav import Navigation, Sections
from certificat.modules.management import HealthStatus
from certificat.modules.perms import Perms
from certificat.settings.dynamic import (
    ACMEFinalizerSettings,
    CERTINextACMEFinalizerSettings,
    FinalizerSettings,
    LocalFinalizerSettings,
)

from ..helpers import client_with_perms, gen_user


def checklist_item(response, title):
    return next(i for i in response.context["checklist"] if i.title == title)


def health_check(response, name):
    return next(c for c in response.context["health_checks"] if c.name == name)


@pytest.mark.django_db
def test_urls():
    assert reverse(Sections.Admin.value) == "/admin/"
    assert reverse("admin-users") == "/admin/users/"
    assert reverse("admin-user", args=[1]) == "/admin/users/1/"
    assert reverse("admin:index") == "/admin/backend/"


@pytest.mark.django_db
def test_anonymous_redirected(web_client: Client):
    assert web_client.get(reverse(Sections.Admin.value)).status_code == 302


def admin_nav_visible(user) -> bool:
    request = RequestFactory().get("/")
    request.user = user
    return Navigation.indexed_top_level_nav[Sections.Admin].test_func(request)


def menu_entries(menu: management.ManagementMenu) -> dict[str, list[str]]:
    """Flattens the menu to {category: [link destinations]}, leaving out
    categories the user has no links in."""
    return {
        c.name: [link.destination for link in c.links]
        for c in menu.categories_with_entries()
    }


@pytest.mark.django_db
def test_requires_power_user(authenticated_web_client: Client):
    assert (
        authenticated_web_client.get(reverse(Sections.Admin.value)).status_code == 403
    )

    user = authenticated_web_client.get(
        reverse(Sections.Dashboard.value)
    ).wsgi_request.user
    assert not admin_nav_visible(user)
    assert menu_entries(management.build_menu(user)) == {}
    assert not admin_nav_visible(AnonymousUser())


@pytest.mark.django_db
@pytest.mark.parametrize(
    "perms, expected",
    [
        (
            [Perms.VIEW_USERS],
            {"Users": ["admin-users", "admin-groups"]},
        ),
        (
            [Perms.EDIT_TOS],
            {"Documentation": ["edit-tos"]},
        ),
        (
            [Perms.EDIT_USAGE],
            {"Documentation": ["edit-usage"]},
        ),
        (
            [Perms.EDIT_TOS, Perms.EDIT_USAGE],
            {"Documentation": ["edit-tos", "edit-usage"]},
        ),
    ],
)
def test_menu_follows_permissions(perms, expected):
    client = client_with_perms(*perms)
    user = client.test_user
    expected = {
        category: [reverse(name) for name in names]
        for category, names in expected.items()
    }

    menu = management.build_menu(user)
    assert menu_entries(menu) == expected
    # Empty categories are kept but not rendered
    assert [c.name for c in menu.categories] == [
        "Users",
        "Documentation",
        "Low-level Admin",
    ]

    response = client.get(reverse(Sections.Admin.value))
    assert response.status_code == 200
    assert response.context["menu"] == menu

    # The nav links to the management page
    assert admin_nav_visible(user)


@pytest.fixture
def staff_client() -> Client:
    # Matches how configured administrators are created at login
    return client_with_perms(is_superuser=True, is_staff=True)


@pytest.mark.django_db
def test_superuser_sees_everything(staff_client: Client):
    response = staff_client.get(reverse(Sections.Admin.value))
    assert response.status_code == 200
    assert menu_entries(response.context["menu"]) == {
        "Users": [reverse("admin-users"), reverse("admin-groups")],
        "Documentation": [reverse("edit-tos"), reverse("edit-usage")],
        "Low-level Admin": [reverse("admin:index")],
    }
    assert admin_nav_visible(staff_client.test_user)


@pytest.mark.django_db
def test_backend_link_requires_staff():
    # Superusers without staff can't reach the Django admin, so it isn't offered
    superuser = gen_user(is_superuser=True)
    assert "Low-level Admin" not in menu_entries(management.build_menu(superuser))

    # Staff alone can reach the management page, which only offers the backend
    staff = gen_user(is_staff=True)
    assert admin_nav_visible(staff)
    menu = management.build_menu(staff)
    assert menu_entries(menu) == {"Low-level Admin": [reverse("admin:index")]}
    (backend,) = menu.categories_with_entries()[0].links
    assert backend.name == "Django Backend"
    assert backend.subtext

    client = Client()
    client.force_login(staff)
    response = client.get(reverse(Sections.Admin.value))
    assert response.status_code == 200
    assert response.context["menu"] == menu


@pytest.mark.django_db
def test_backend_admin_moved(staff_client: Client):
    response = staff_client.get("/admin/backend/")
    assert response.status_code == 200
    assert response.resolver_match.namespace == "admin"


@pytest.mark.django_db
def test_checklist_content_items(authenticated_su_web_client: Client):
    url = reverse(Sections.Admin.value)
    response = authenticated_su_web_client.get(url)
    assert not checklist_item(response, "Write the terms of service").done
    assert not checklist_item(response, "Write usage instructions").done
    assert checklist_item(response, "Write the terms of service").link == reverse(
        "edit-tos"
    )

    db.TermsOfService.objects.create(text="terms")
    db.Usage.objects.create(text="usage")
    response = authenticated_su_web_client.get(url)
    assert checklist_item(response, "Write the terms of service").done
    assert checklist_item(response, "Write usage instructions").done


@pytest.mark.django_db
def test_checklist_link_hidden_without_perm():
    client = client_with_perms(Perms.VIEW_USERS)
    response = client.get(reverse(Sections.Admin.value))
    assert checklist_item(response, "Write the terms of service").link is None
    # Only superusers can edit groups
    assert checklist_item(response, "Delegate permissions").link is None


@pytest.mark.django_db
def test_checklist_finalizer(authenticated_su_web_client: Client):
    # The test configuration uses the local finalizer, which is trial only
    response = authenticated_su_web_client.get(reverse(Sections.Admin.value))
    item = checklist_item(response, "Configure an upstream finalizer")
    assert not item.done
    assert "'local'" in item.current_description

    # Not configurable, so it can't be switched on in config.yml
    assert "production_ready" not in FinalizerSettings.model_fields
    assert ACMEFinalizerSettings.production_ready
    assert CERTINextACMEFinalizerSettings.production_ready
    assert not LocalFinalizerSettings.production_ready

    done = management.ChecklistItem("t", "not done", True, done_description="done")
    assert done.current_description == "done"


@pytest.mark.django_db
def test_checklist_delegation(authenticated_su_web_client: Client):
    url = reverse(Sections.Admin.value)
    response = authenticated_su_web_client.get(url)
    assert not checklist_item(response, "Delegate permissions").done

    assert checklist_item(response, "Delegate permissions").link == reverse(
        "admin-groups"
    )

    # Unrelated permissions and legacy direct grants don't count
    user = gen_user()
    user.user_permissions.add(Perms.VIEW_ALL_ORDERS.get_permission())
    unrelated = Group.objects.create(name="unrelated")
    unrelated.permissions.add(
        Permission.objects.get(content_type__app_label="auth", codename="delete_user")
    )
    user.groups.add(unrelated)
    response = authenticated_su_web_client.get(url)
    assert not checklist_item(response, "Delegate permissions").done

    group = Group.objects.create(name="ops")
    group.permissions.add(Perms.VIEW_ALL_ORDERS.get_permission())
    user.groups.add(group)
    response = authenticated_su_web_client.get(url)
    assert checklist_item(response, "Delegate permissions").done


@pytest.mark.django_db
def test_health_checks(authenticated_su_web_client: Client):
    url = reverse(Sections.Admin.value)
    response = authenticated_su_web_client.get(url)
    assert health_check(response, "Task worker").status == HealthStatus.WARNING
    assert health_check(response, "Order processing").status == HealthStatus.OK

    management.record_task_worker_heartbeat()
    response = authenticated_su_web_client.get(url)
    assert health_check(response, "Task worker").status == HealthStatus.OK

    db.Config.set(management.TASK_WORKER_HEARTBEAT_KEY, str(time.time() - 3600))
    response = authenticated_su_web_client.get(url)
    assert health_check(response, "Task worker").status == HealthStatus.ERROR


@pytest.mark.django_db
def test_failing_health_check_is_reported():
    def boom():
        raise RuntimeError("nope")

    check = management._check("Broken", boom)
    assert check.status == HealthStatus.ERROR
    assert "RuntimeError" in check.detail


@pytest.mark.django_db
def test_stuck_orders(authenticated_su_web_client: Client):
    url = reverse(Sections.Admin.value)
    account = db.Account.objects.create(
        name="stuck", status=AccountStatus.valid, jwk="{}", jwk_thumbprint="stuck"
    )
    order = db.Order.objects.create(
        account=account,
        name="stuck-order",
        status=OrderStatus.processing,
        expires=timezone.now(),
    )

    # Recently updated orders are still in flight
    response = authenticated_su_web_client.get(url)
    assert health_check(response, "Order processing").status == HealthStatus.OK

    db.Order.objects.filter(pk=order.pk).update(
        updated_at=timezone.now() - management.STUCK_ORDER_AGE * 2
    )
    response = authenticated_su_web_client.get(url)
    assert health_check(response, "Order processing").status == HealthStatus.WARNING
