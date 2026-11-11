import logging

from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from certificat.modules import management
from certificat.modules.groups import (
    group_perms_by_category,
    search_groups,
    set_group_perms,
)
from certificat.modules.perms import (
    MANAGEABLE_PERMS_BY_VALUE,
    Gates,
    PermissionGate,
    Perms,
    require_gate,
)
from certificat.modules.users import search_users, user_perms_by_category
from certificat.utils import paginate

from ..nav import BreadCrumbs, Sections, build_breadcrumbs
from .base import ViewBase

logger = logging.getLogger(__name__)


class AdminViewBase(ViewBase):
    """Base for the pages under /admin/. Requires permission to view users
    unless a subclass says otherwise."""

    section = Sections.Admin

    def admin_breadcrumbs(self, *crumbs) -> BreadCrumbs:
        return build_breadcrumbs(("Admin", reverse(Sections.Admin.value)), *crumbs)


class ManagementView(AdminViewBase):
    def get_breadcrumbs(self, **kwargs):
        return build_breadcrumbs("Admin")

    @require_gate(Gates.CAN_ACCESS_MANAGEMENT)
    def get(self, request: HttpRequest):
        context = self.get_context_data(
            checklist=management.setup_checklist(request.user, self.settings),
            health_checks=management.health_checks(),
            menu=management.build_menu(request.user),
        )
        return render(request, "certificat/admin.html", context)


class UsersView(AdminViewBase):
    def get_breadcrumbs(self, **kwargs):
        return self.admin_breadcrumbs("Users")

    @require_gate(Gates.VIEW_USERS)
    def get(self, request: HttpRequest):
        users_paginator, users_page = paginate(
            search_users(request.GET.get("filter")),
            request.GET.get("page", 1),
        )
        context = self.get_context_data(
            users={"paginator": users_paginator, "page": users_page}
        )
        return render(request, "certificat/users.html", context)


class UserView(AdminViewBase):
    def get_breadcrumbs(self, **kwargs):
        return self.admin_breadcrumbs(("Users", reverse("admin-users")), "Profile")

    @require_gate(Gates.VIEW_USERS)
    def get(self, request: HttpRequest, user_id: int):
        profile = get_object_or_404(User, pk=user_id)
        context = self.get_context_data(
            profile=profile,
            groups=profile.groups.order_by("name"),
            perms_by_category=user_perms_by_category(profile),
        )
        return render(request, "certificat/user.html", context)


class GroupsView(AdminViewBase):
    def get_breadcrumbs(self, **kwargs):
        return self.admin_breadcrumbs("Groups")

    @require_gate(Gates.VIEW_GROUPS)
    def get(self, request: HttpRequest):
        groups_paginator, groups_page = paginate(
            search_groups(request.GET.get("filter")),
            request.GET.get("page", 1),
        )
        context = self.get_context_data(
            groups={"paginator": groups_paginator, "page": groups_page}
        )
        return render(request, "certificat/groups.html", context)


class GroupView(AdminViewBase):
    MAX_MEMBERS_SHOWN = 50

    def get_breadcrumbs(self, **kwargs):
        return self.admin_breadcrumbs(("Groups", reverse("admin-groups")), "Group")

    @require_gate(Gates.VIEW_GROUPS)
    def get(self, request: HttpRequest, group_id: int):
        group = get_object_or_404(Group, pk=group_id)
        members = group.user_set.order_by("username")

        context = self.get_context_data(
            group=group,
            members=members[: self.MAX_MEMBERS_SHOWN],
            member_count=members.count(),
            perms_by_category=group_perms_by_category(group),
            can_edit=PermissionGate.evaluate(request.user, Gates.EDIT_GROUPS),
        )
        return render(request, "certificat/group.html", context)

    @require_gate(Gates.EDIT_GROUPS)
    def post(self, request: HttpRequest, group_id: int):
        group = get_object_or_404(Group, pk=group_id)

        selected_values = set(request.POST.getlist("perms"))
        if not selected_values <= MANAGEABLE_PERMS_BY_VALUE.keys():
            return HttpResponse(status=400)

        added, removed = set_group_perms(
            group, {Perms(value) for value in selected_values}
        )

        if added or removed:
            messages.success(request, "Group permissions updated.")
            logger.info(
                "User %s updated permissions for group %s, added: %s, removed: %s",
                request.user.username,
                group.name,
                ",".join(sorted(added)) or "none",
                ",".join(sorted(removed)) or "none",
            )
        else:
            messages.info(request, "No permission changes to save.")

        return HttpResponseRedirect(reverse("admin-group", args=[group.id]))
