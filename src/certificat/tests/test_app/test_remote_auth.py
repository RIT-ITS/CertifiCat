from django.urls import reverse

from certificat.modules.html.nav import Sections
from certificat.settings.dynamic import ApplicationSettings, RemoteAuthSettings
import pytest
from django.test import Client
from django.contrib.auth.models import User


class TestRemoteAuth:
    USER_HEADER = "USER"
    LOGIN_URL = "/remote/login/"

    @pytest.fixture(autouse=True)
    def setup_class_members(self, settings):
        ApplicationSettings.get().authentication = RemoteAuthSettings(
            user_header="HTTP_" + self.USER_HEADER,
            redirect_template="http://example.com/?rd={redirect}",
        )

        settings.AUTHENTICATION_BACKENDS = ["certificat.auth.RemoteUserBackend"]
        settings.LOGIN_URL = self.LOGIN_URL
        settings.MIDDLEWARE.append(
            "certificat.middleware.CustomHeaderRemoteUserMiddleware"
        )

    def test_anonymous(self, web_client: Client):
        response = web_client.get(reverse(Sections.Accounts.value))

        assert response.status_code == 302
        assert self.LOGIN_URL in response.url

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

    def test_redirect(self, web_client: Client):
        response = web_client.get(reverse(Sections.Accounts.value))

        assert self.LOGIN_URL in response.url
        redirect = web_client.get(response.url)
        assert redirect.url == "http://example.com/?rd=/accounts/"

    def test_unprotected_resources(self, web_client: Client):
        response = web_client.get(reverse("acme:directory"))
        assert response.status_code == 200
        assert "newAccount" in response.json()

    @pytest.mark.django_db
    def test_reconcile_superuser(self, web_client: Client):
        """Test that an average user is not a superuser unless they're in the admin list."""
        auth_settings: RemoteAuthSettings = ApplicationSettings.get().authentication
        username = "remusr"

        web_client.get(
            reverse(Sections.Accounts.value), headers={self.USER_HEADER: username}
        )
        user = User.objects.get(username=username)
        user.refresh_from_db()
        assert not user.is_superuser

        web_client.logout()
        auth_settings.administrators = [user.username, "dummy-user"]
        web_client.get(
            reverse(Sections.Accounts.value), headers={self.USER_HEADER: username}
        )
        user.refresh_from_db()
        assert user.is_superuser

        web_client.logout()
        auth_settings.administrators = ["dummy-user"]
        web_client.get(
            reverse(Sections.Accounts.value), headers={self.USER_HEADER: username}
        )
        user.refresh_from_db()
        assert not user.is_superuser

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
