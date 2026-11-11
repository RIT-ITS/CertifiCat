"""Setup checklist and health checks shown on the management page."""

import logging
import time
from dataclasses import dataclass, field
from datetime import timedelta
from enum import StrEnum

from acmev2.models import OrderStatus
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from certificat.modules.acme import models as db
from certificat.modules.perms import manageable_permissions
from certificat.settings.dynamic import ApplicationSettings

from .perms import Gates, PermissionGate, UserPermissionGate

logger = logging.getLogger(__name__)

TASK_WORKER_HEARTBEAT_KEY = "task-worker-heartbeat"
TASK_WORKER_HEARTBEAT_MAX_AGE = 180  # seconds
STUCK_ORDER_AGE = timedelta(hours=1)


def record_task_worker_heartbeat():
    """Called from the task worker so the web process can tell it is alive.
    The worker can run in a different container than the web UI, so this is
    stored in the database rather than on disk."""
    db.Config.set(
        TASK_WORKER_HEARTBEAT_KEY,
        str(time.time()),
        "Last time the task worker reported in.",
    )


@dataclass
class ProtectedLink:
    name: str
    destination: str
    subtext: str = ""


@dataclass
class MenuCategory:
    name: str
    links: list[ProtectedLink] = field(default_factory=list)


@dataclass
class ManagementMenu:
    """A menu with categories, sub-elements, and permission-based rendering."""

    categories: list[MenuCategory]

    def categories_with_entries(self):
        return [c for c in self.categories if len(c.links) > 0]


def build_menu(user: User):
    acct_category = MenuCategory("Users")
    gate = UserPermissionGate(user)

    if gate.evaluate(Gates.VIEW_USERS):
        acct_category.links.append(ProtectedLink("Users", reverse("admin-users")))
    if gate.evaluate(Gates.VIEW_GROUPS):
        acct_category.links.append(ProtectedLink("Groups", reverse("admin-groups")))

    docs_category = MenuCategory("Documentation")
    if gate.evaluate(Gates.EDIT_TOS):
        docs_category.links.append(
            ProtectedLink("Terms of Service", reverse("edit-tos"))
        )

    if gate.evaluate(Gates.EDIT_USAGE):
        docs_category.links.append(ProtectedLink("Usage", reverse("edit-usage")))

    low_level_category = MenuCategory("Low-level Admin")
    if user.is_staff:
        low_level_category.links.append(
            ProtectedLink(
                "Django Backend", reverse("admin:index"), subtext="Here be dragons"
            )
        )

    return ManagementMenu([acct_category, docs_category, low_level_category])


@dataclass
class ChecklistItem:
    title: str
    description: str
    done: bool
    link: str | None = None
    link_text: str | None = None
    optional: bool = False
    # Shown instead of `description` once the item is done
    done_description: str | None = None

    @property
    def current_description(self) -> str:
        if self.done and self.done_description:
            return self.done_description
        return self.description


def setup_checklist(user: User, settings: ApplicationSettings) -> list[ChecklistItem]:
    gate = UserPermissionGate(user)
    tos_link = reverse("edit-tos") if gate.evaluate(Gates.EDIT_TOS) else None
    usage_link = reverse("edit-usage") if gate.evaluate(Gates.EDIT_USAGE) else None
    groups_link = (
        reverse("admin-groups")
        if PermissionGate.evaluate(user, Gates.EDIT_GROUPS)
        else None
    )

    delegated = User.objects.filter(
        is_superuser=False,
        is_active=True,
        groups__permissions__in=manageable_permissions(),
    ).exists()

    notifications = settings.notifications
    notifications_configured = bool(
        notifications
        and (
            notifications.on_finalization_success or notifications.on_finalization_error
        )
    )

    deprecations = settings.get_deprecations()

    return [
        ChecklistItem(
            "Write the terms of service",
            "Users must agree to the terms of service before creating an account.",
            db.TermsOfService.objects.exists(),
            tos_link,
            "Edit ToS",
        ),
        ChecklistItem(
            "Write usage instructions",
            "The usage page explains how to configure ACME clients against this server.",
            db.Usage.objects.exists(),
            usage_link,
            "Edit usage",
        ),
        ChecklistItem(
            "Configure an upstream finalizer",
            f"The '{settings.finalizer.type}' finalizer is not supported except "
            "on a trial basis.",
            settings.finalizer.production_ready,
            done_description="A production finalizer has been configured.",
        ),
        ChecklistItem(
            "Delegate permissions",
            "Grant permissions to at least one group with members who aren't "
            "superusers, so day to day administration doesn't require superuser "
            "access.",
            delegated,
            groups_link,
            "Manage groups",
        ),
        ChecklistItem(
            "Configure notifications",
            "Set certificat.notifications to be alerted when finalization succeeds "
            "or fails.",
            notifications_configured,
            optional=True,
        ),
        ChecklistItem(
            "Remove deprecated settings",
            "; ".join(deprecations)
            if deprecations
            else "The configuration file doesn't use any deprecated settings.",
            not deprecations,
        ),
    ]


class HealthStatus(StrEnum):
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class HealthCheck:
    name: str
    status: HealthStatus
    detail: str


def _check(name: str, func) -> HealthCheck:
    try:
        status, detail = func()
    except Exception as e:
        logger.exception("Health check %s failed", name)
        status, detail = HealthStatus.ERROR, f"Check failed: {e.__class__.__name__}"
    return HealthCheck(name, status, detail)


def _check_task_worker():
    heartbeat = db.Config.get(TASK_WORKER_HEARTBEAT_KEY)
    if heartbeat is None:
        return (
            HealthStatus.WARNING,
            "The task worker hasn't reported in yet. It reports once a minute.",
        )

    age = time.time() - float(heartbeat)
    if age > TASK_WORKER_HEARTBEAT_MAX_AGE:
        return (
            HealthStatus.ERROR,
            (
                f"Last report was {int(age // 60)} minutes ago. Orders won't be "
                "validated or finalized until the worker is running."
            ),
        )
    return HealthStatus.OK, f"Last report {int(age)} seconds ago."


def _check_stuck_orders():
    cutoff = timezone.now() - STUCK_ORDER_AGE
    stuck = db.Order.objects.filter(
        status=OrderStatus.processing, updated_at__lt=cutoff
    ).count()
    if stuck:
        return (
            HealthStatus.WARNING,
            (
                f"{stuck} order(s) have been processing for over an hour. Check "
                "the finalizer and task worker logs."
            ),
        )
    return HealthStatus.OK, "No orders stuck in processing."


def health_checks() -> list[HealthCheck]:
    return [
        _check("Task worker", _check_task_worker),
        _check("Order processing", _check_stuck_orders),
    ]
