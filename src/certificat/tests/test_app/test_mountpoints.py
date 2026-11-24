from urllib.parse import urlsplit

import inject
import pytest
from acmev2.services import ACMEEndpoint, IDirectoryService
from django.test import Client
from django.urls import reverse

from certificat.modules.html.nav import Sections
from certificat.settings.dynamic import ApplicationSettings


@pytest.mark.django_db
def test_mountpoints_unaltered(reload_urls):
    app_settings = ApplicationSettings.get()
    web_prefix = ""
    acme_prefix = ""

    # If you change the web_prefix, web URLs should load from there
    app_settings.web_ui_mountpoint = web_prefix
    # Likewise ACME URLs should change
    app_settings.web_acme_mountpoint = acme_prefix

    reload_urls()

    # base expectations
    url = reverse(Sections.Accounts.value)
    assert urlsplit(url).path == "/accounts/"

    url = reverse("directory")
    assert urlsplit(url).path == "/directory"


@pytest.mark.django_db
def test_mountpoints_altered(reload_urls):
    app_settings = ApplicationSettings.get()
    web_prefix = "web-prefix/"
    acme_prefix = "acme-prefix/"

    # If you change the web_prefix, web URLs should load from there
    app_settings.web_ui_mountpoint = web_prefix
    # Likewise ACME URLs should change
    app_settings.web_acme_mountpoint = acme_prefix

    reload_urls()

    url = reverse(Sections.Accounts.value)
    assert web_prefix in url

    url = reverse("directory")
    assert urlsplit(url).path == "/" + acme_prefix + "directory"

    url = reverse("acme:new-nonce")
    assert urlsplit(url).path == "/" + acme_prefix + "newNonce"

    directory_service = inject.instance(IDirectoryService)
    dir_svc_url = directory_service.url_for(ACMEEndpoint.newAccount)

    # Test that the urlbuilder in the directory service also uses the new mountpoint
    assert urlsplit(dir_svc_url).path == "/" + acme_prefix + "newAcct"


@pytest.mark.django_db
def test_mountpoints_equivalency(reload_urls):
    app_settings = ApplicationSettings.get()

    for prefix in ["web", "/web", "/web/"]:
        app_settings.web_ui_mountpoint = ApplicationSettings.validate_mountpoint(prefix)

        reload_urls()

        url = reverse(Sections.Accounts.value)
        url = reverse(Sections.Accounts.value)
        assert urlsplit(url).path == "/web/accounts/", (
            f"{prefix} produced incorrect url"
        )


@pytest.mark.django_db
def test_directory_resolves(reload_urls, web_client: Client):
    app_settings = ApplicationSettings.get()
    web_prefix = "web-prefix/"
    acme_prefix = "acme-prefix/"

    # If you change the web_prefix, web URLs should load from there
    app_settings.web_ui_mountpoint = web_prefix
    # Likewise ACME URLs should change
    app_settings.web_acme_mountpoint = acme_prefix

    reload_urls()

    url = reverse("directory")
    assert urlsplit(url).path == "/" + acme_prefix + "directory"

    response = web_client.get(url)
    assert response.status_code == 200
    assert "newAccount" in response.json()
