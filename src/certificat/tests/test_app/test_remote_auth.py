from dataclasses import dataclass, field
from typing import List

from django.urls import reverse

from certificat.modules.html.nav import Sections
from certificat.settings.dynamic import ApplicationSettings, RemoteAuthSettings
import pytest
from django.test import Client
from django.contrib.auth.models import Group, User


class TestRemoteAuth:
    USER_HEADER = "USER"

    @pytest.fixture(autouse=True)
    def setup_class_members(self, settings):
        ApplicationSettings.get().authentication = RemoteAuthSettings(
            user_header="HTTP_" + self.USER_HEADER,
            redirect_template="http://example.com/?rd={redirect}",
        )

        settings.AUTHENTICATION_BACKENDS = ["certificat.auth.RemoteUserBackend"]
        settings.LOGIN_URL = reverse("remote-login-redirect")
        settings.MIDDLEWARE.append(
            "certificat.middleware.CustomHeaderRemoteUserMiddleware"
        )

    def test_anonymous(self, web_client: Client):
        response = web_client.get(reverse(Sections.Accounts.value))

        assert response.status_code == 302
        assert reverse("remote-login-redirect") in response.url

    @pytest.mark.django_db
    def test_authenticated(self, web_client: Client):
        response = web_client.get(
            reverse(Sections.Accounts.value), headers={self.USER_HEADER: "remusr"}
        )

        assert response.status_code == 200
        assert response.context["user"].username == "remusr"

    @pytest.mark.django_db
    def test_authenticated_with_mappings(self, web_client: Client):
        mappings = {
            "HTTP_USER_EMAIL": ["email"],
            "HTTP_USER_FIRSTNAME": ["first_name"],
            "HTTP_USER_LASTNAME": ["last_name"],
        }
        alt_mappings = {
            "HTTP_USER_EMAIL": "email",
            "HTTP_USER_FIRSTNAME": "first_name",
            "HTTP_USER_LASTNAME": "last_name",
        }

        auth_settings: RemoteAuthSettings = ApplicationSettings.get().authentication

        for mapping in [mappings, alt_mappings]:
            auth_settings.attribute_mapping = mapping
            web_client.logout()
            headers = {
                self.USER_HEADER: "remusr",
                "USER_EMAIL": "remusr@nomail.com",
                "USER_FIRSTNAME": "First",
                "USER_LASTNAME": "Last",
            }
            response = web_client.get(reverse(Sections.Accounts.value), headers=headers)

            assert response.status_code == 200

            user = response.context["user"]
            assert user.username == headers[self.USER_HEADER]
            assert user.first_name == headers["USER_FIRSTNAME"]
            assert user.last_name == headers["USER_LASTNAME"]
            assert user.email == headers["USER_EMAIL"]

            user.first_name = ""
            user.last_name = ""
            user.email = ""

            user.save()

    @pytest.mark.django_db
    def test_header_removed(self, web_client: Client):
        response = web_client.get(
            reverse(Sections.Accounts.value), headers={self.USER_HEADER: "remusr"}
        )

        assert response.status_code == 200

        response = web_client.get(reverse(Sections.Accounts.value))
        assert response.status_code == 302

    @pytest.mark.django_db
    def test_user_changed(self, web_client: Client):
        response = web_client.get(
            reverse(Sections.Accounts.value), headers={self.USER_HEADER: "remusr"}
        )

        first_user = response.context["user"]

        response = web_client.get(
            reverse(Sections.Accounts.value), headers={self.USER_HEADER: "remusr2"}
        )

        second_user = response.context["user"]

        assert first_user.username != second_user.username

    @pytest.mark.django_db
    def test_redirect(self, web_client: Client):
        web_client.logout()

        response = web_client.get(reverse(Sections.Accounts.value))

        assert reverse("remote-login-redirect") in response.url
        redirect = web_client.get(response.url)

        assert redirect.url == "http://example.com/?rd=" + reverse(
            Sections.Accounts.value
        )

    @pytest.mark.django_db
    def test_unprotected_resources(self, web_client: Client):
        web_client.logout()
        response = web_client.get(reverse("directory"))
        assert response.status_code == 200
        assert "newAccount" in response.json()

    @dataclass
    class ReconcileSuperTestCase:
        admins: List[str]
        admin_groups: List[str]
        username: str
        expected_admin: bool
        initial_groups: List[str] = field(default_factory=list)
        initial_superuser: bool = False

    @pytest.mark.django_db
    def test_reconcile_superuser(self, web_client: Client):
        """Test that an average user is not a superuser unless they're in the admin list. A lot of this is redundant from test_login_hooks"""
        auth_settings: RemoteAuthSettings = ApplicationSettings.get().authentication
        username = "remusr"

        case = TestRemoteAuth.ReconcileSuperTestCase

        test_cases = [
            # ensure basic user doesn't have access
            case(admins=[], admin_groups=[], username=username, expected_admin=False),
            # ensure user is superuser when added manually
            case(
                admins=[username],
                admin_groups=[],
                username=username,
                expected_admin=True,
            ),
            # ensure superuser is removed when removed from admins
            case(
                admins=[],
                admin_groups=[],
                username=username,
                expected_admin=False,
                initial_superuser=True,
            ),
            # ensure superuser is added when user is in group
            case(
                admins=[],
                admin_groups=["admin-group"],
                username=username,
                expected_admin=True,
                initial_groups=["admin-group"],
            ),
            # ensure superuser is removed when user is not in group
            case(
                admins=[],
                admin_groups=["admin-group"],
                username=username,
                expected_admin=False,
                initial_superuser=True,
                initial_groups=["nonadmin-group"],
            ),
            # ensure erroneous groups are ignored
            case(
                admins=["different-usr"],
                admin_groups=["admin-group"],
                username=username,
                expected_admin=False,
                initial_groups=["nonadmin-group", "another-nonadmin-group"],
            ),
        ]

        for idx, case in enumerate(test_cases):
            try:
                initial_user = User.objects.get(username=username)
                initial_user.groups.clear()
                initial_user.is_superuser = case.initial_superuser
                for group_name in case.initial_groups:
                    group, _ = Group.objects.get_or_create(name=group_name)
                    initial_user.groups.add(group)
                initial_user.save()
            except User.DoesNotExist:
                initial_user = None

            auth_settings.administrators_groups = case.admin_groups
            auth_settings.administrators = case.admins
            web_client.get(
                reverse(Sections.Accounts.value), headers={self.USER_HEADER: username}
            )
            user = User.objects.get(username=username)
            assert user.is_superuser == case.expected_admin, f"Case {idx + 1} failed."

            web_client.logout()

    @pytest.mark.django_db
    def test_group_mapping(self, web_client: Client):
        auth_settings: RemoteAuthSettings = ApplicationSettings.get().authentication
        auth_settings.groups_header = "HTTP_GROUPS"

        tests = (
            (
                r"group1;group2;weird\;group;group4",
                ["group1", "group2", "weird;group", "group4"],
            ),
            (
                "group1;group2",
                [
                    "group1",
                    "group2",
                ],
            ),
            (
                "group1",
                [
                    "group1",
                ],
            ),
            (
                "group1;",
                [
                    "group1",
                ],
            ),
            (
                "",
                [],
            ),
        )

        username = "remusr"
        for header_val, groups in tests:
            web_client.get(
                reverse(Sections.Accounts.value),
                headers={
                    self.USER_HEADER: username,
                    "GROUPS": header_val,
                },
            )

            user = User.objects.get(username=username)

            assert sorted([g.name for g in user.groups.all()]) == sorted(
                [f"{auth_settings.group_sync_prefix}{g}" for g in groups]
            )
            web_client.logout()
