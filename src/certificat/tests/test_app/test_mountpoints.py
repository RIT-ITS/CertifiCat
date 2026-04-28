from certificat.modules.html.nav import Sections
from certificat.settings.dynamic import ApplicationSettings
from django.urls import reverse
import inject
import pytest
from urllib.parse import urlsplit
from acmev2.services import ACMEEndpoint, IDirectoryService


@pytest.mark.django_db
def test_mountpoints_unaltered():

    web_prefix = "web-prefix/"

    # base expectations
    url = reverse(Sections.Accounts.value)
    assert web_prefix not in url

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
