from django.urls import reverse

from certificat.modules.html.nav import Sections
from certificat.settings.dynamic import ApplicationSettings, RemoteAuthSettings
import pytest
from django.test import Client


class TestRemoteAuth:
    USER_HEADER = "USER"
    LOGIN_URL = "/remote/login"

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
