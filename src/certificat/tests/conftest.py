from certificat.modules.acme.services import (
    AccountService,
    AuthorizationService,
    CertService,
    ChallengeService,
    DirectoryService,
    NonceService,
    OrderService,
)
import inject
import pytest
from urllib.parse import urlparse

from acmev2.services import (
    IDirectoryService,
    INonceService,
    IAccountService,
    IAuthorizationService,
    IOrderService,
    IChallengeService,
    ICertService,
)
import io
import acme.client
from django.test import Client
import josepy
import requests
import requests.adapters
import urllib3
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

ROOT_URL = "http://mock.me"


class TestDirectoryService(DirectoryService):
    root_url = f"{ROOT_URL}/acme"


@pytest.fixture(autouse=True)
def setup():
    import dnsmock

    # I have no idea why these are necessary. If they don't exist then DNS resolution
    # will intermittently fail. Suspect it has something to do with Docker networking
    # and embedded DNS but it's not important enough to fix.
    dnsmock.bind_ip("acme.localhost", 443, "127.0.0.1")
    dnsmock.bind_ip("acme.localhost", 80, "127.0.0.1")
    dnsmock.bind_ip("mock.me", 80, "127.0.0.1")

    from certificat.settings.dynamic import ACMESettings, ApplicationSettings

    bindings = [
        (INonceService, NonceService()),
        (IDirectoryService, TestDirectoryService()),
        (IAccountService, AccountService()),
        (IOrderService, OrderService()),
        (IAuthorizationService, AuthorizationService()),
        (IChallengeService, ChallengeService()),
        (ICertService, CertService()),
        (ACMESettings, ACMESettings()),
        (ApplicationSettings, ApplicationSettings()),
    ]
    inject.configure(
        lambda binder: [binder.bind(api, impl) for api, impl in bindings],
        bind_in_runtime=False,
        clear=True,
    )


class LocalACMEAdapter(requests.adapters.HTTPAdapter):
    def send(
        self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None
    ):
        c = Client()
        url_parts = urlparse(request.url)

        django_response = getattr(c, request.method.lower())(
            path=request.path_url,
            data=request.body,
            headers=request.headers,
            content_type=request.headers.get("Content-Type"),
            SERVER_NAME=url_parts.netloc,
        )

        content = io.BytesIO(django_response.content)
        urllib_response = urllib3.HTTPResponse(
            content,
            django_response.headers,
            django_response.status_code,
            preload_content=False,
        )

        return self.build_response(
            request,
            urllib_response,
        )


@pytest.fixture
def acme_client():
    return gen_acme_client()


def gen_acme_client():
    rsa_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )
    account_key = josepy.JWKRSA(key=rsa_key)

    net = acme.client.ClientNetwork(account_key, user_agent="certificat.tests")
    net.session.mount(f"{ROOT_URL}/acme/", LocalACMEAdapter())
    directory_service = inject.instance(IDirectoryService)

    return acme.client.ClientV2(
        acme.client.messages.Directory.from_json(directory_service.get_directory()),
        net=net,
    )
