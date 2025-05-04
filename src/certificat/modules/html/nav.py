from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable

from django.http import HttpRequest
from django.urls import reverse


class Sections(str, Enum):
    Dashboard = "DASHBOARD"
    Usage = "USAGE"
    Accounts = "ACCOUNTS"
    Orders = "ORDERS"
    Certificates = "CERTIFICATES"
    TOS = "TOS"
    Admin = "ADMIN"


class NavItem:
    def __init__(
        self,
        section: Sections,
        name: str,
        test: Callable[[HttpRequest], bool] = None,
    ):
        self.section = section
        self.name = name
        self.test_func = test

    def bind_request(self, request: HttpRequest):
        self.request = request

    def can_access(self) -> bool:
        return self.test_func(self.request) if self.test_func else True

    def is_selected(self) -> bool:
        try:
            return self.request.resolver_match.func.view_class.section == self.section
        except:  # noqa: E722
            return False

    def path_prefix(self) -> str:
        return reverse(self.section.value)


def is_admin_test(request: HttpRequest):
    # TODO: Make admin group
    return request.user.is_superuser


class Navigation:
    top_level_nav = [
        NavItem(Sections.Dashboard, "Dashboard"),
        NavItem(Sections.Accounts, "Accounts"),
        NavItem(Sections.Usage, "Usage"),
        NavItem(Sections.Certificates, "Certificates"),
        NavItem(Sections.TOS, "Terms of Service"),
        NavItem(Sections.Admin, "Admin", is_admin_test),
    ]
    indexed_top_level_nav = {n.section: n for n in top_level_nav}

    def __init__(self, request: HttpRequest):
        for nav in self.top_level_nav:
            nav.bind_request(request)


@dataclass
class BreadCrumb:
    name: str
    link: str | None = None


@dataclass
class BreadCrumbs:
    data: list[BreadCrumb]


def build_breadcrumbs(*crumbs: list[Any]) -> BreadCrumbs:
    return BreadCrumbs(
        [BreadCrumb("CertifiCat", "/")]
        + [
            BreadCrumb(args) if isinstance(args, str) else BreadCrumb(*args)
            for args in crumbs
        ]
    )
