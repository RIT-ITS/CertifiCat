import time

import pytest
from acmev2.models import AccountStatus, OrderStatus
from django.contrib.auth.models import Group, Permission
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from certificat.modules import management
from certificat.modules.acme import models as db
from certificat.modules.html.nav import Sections
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


@pytest.mark.django_db
def test_requires_power_user(authenticated_web_client: Client):
    admin_url = reverse(Sections.Admin.value)
    assert authenticated_web_client.get(admin_url).status_code == 403

    response = authenticated_web_client.get(reverse(Sections.Dashboard.value))
    assert f'href="{admin_url}"' not in response.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "perm, visible, hidden",
    [
        (
            Perms.VIEW_USERS,
            ["admin-link-users"],
            ["admin-link-tos", "admin-link-backend"],
        ),
        (
            Perms.EDIT_TOS,
            ["admin-link-tos"],
            ["admin-link-users", "admin-link-backend"],
        ),
        (
            Perms.EDIT_USAGE,
            ["admin-link-usage"],
            ["admin-link-users", "admin-link-tos"],
        ),
    ],
)
def test_links_follow_permissions(perm, visible, hidden):
    client = client_with_perms(perm)
    admin_url = reverse(Sections.Admin.value)

    response = client.get(admin_url)
    assert response.status_code == 200
    content = response.content.decode()
    for link in visible:
        assert f'id="{link}"' in content
    for link in hidden:
        assert f'id="{link}"' not in content

    # The nav links to the management page
    response = client.get(reverse(Sections.Dashboard.value))
    assert f'href="{admin_url}"' in response.content.decode()


@pytest.fixture
def staff_client() -> Client:
    # Matches how configured administrators are created at login
    return client_with_perms(is_superuser=True, is_staff=True)


@pytest.mark.django_db
def test_superuser_sees_everything(staff_client: Client):
    response = staff_client.get(reverse(Sections.Admin.value))
    assert response.status_code == 200
    content = response.content.decode()
    for link in ("users", "tos", "usage", "backend"):
        assert f'id="admin-link-{link}"' in content
    assert f'href="{reverse("admin:index")}"' in content


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
