from collections import namedtuple
import acme.messages
from certificat.modules.acme.services import (
    AccountService,
    AuthorizationService,
    CertService,
    ChallengeService,
    DirectoryService,
    NonceService,
    OrderService,
)

from certificat.settings.dynamic import ApplicationSettings
from acmev2.settings import ACMESettings
import inject
import pytest
from urllib.parse import urlparse
from certificat.modules.acme import models as db
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
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from . import helpers

ROOT_URL = "http://mock.me"


class TestDirectoryService(DirectoryService):
    def __init__(self):
        self.root_url = f"{ROOT_URL}/acme"


@pytest.fixture(autouse=True)
def setup():
    import dnsmock

    # I have no idea why these are necessary. If they don't exist then DNS resolution
    # will intermittently fail. Suspect it has something to do with Docker networking
    # and embedded DNS but it's not important enough to fix.
    dnsmock.bind_ip("acme.localhost", 443, "127.0.0.1")
    dnsmock.bind_ip("acme.localhost", 80, "127.0.0.1")
    dnsmock.bind_ip("acme2.localhost", 443, "127.0.0.1")
    dnsmock.bind_ip("acme2.localhost", 80, "127.0.0.1")
    dnsmock.bind_ip("mock.me", 80, "127.0.0.1")

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


@pytest.fixture
def web_client():
    c = Client(enforce_csrf_checks=False)
    return c


@pytest.fixture
def authenticated_web_client():
    c = Client(enforce_csrf_checks=False)
    user = helpers.gen_user()
    c.force_login(user)
    c.test_user = user

    return c


@pytest.fixture
def settings():
    return inject.instance(ApplicationSettings)


@pytest.fixture
def acme_settings():
    return inject.instance(ACMESettings)


NewAcctRet = namedtuple("NewAcctRet", ["response", "binding", "user"])


@pytest.fixture
def acme_newacct(acme_client: acme.client.ClientV2):
    def wrapped(acme_client=acme_client, with_eab=False, binding=None, user=None):
        eab = None

        if with_eab:
            user = helpers.gen_user()

            binding = binding or db.AccountBinding.generate(user, name="test account")

            account_public_key = acme_client.net.key.public_key()
            eab = acme.client.messages.ExternalAccountBinding.from_data(
                account_public_key=account_public_key,
                kid=binding.hmac_id,
                hmac_key=binding.hmac_key,
                directory=acme_client.directory,
            )

        registration = acme.client.messages.NewRegistration.from_data(
            email="email@acme.edu" if not user else user.email,
            terms_of_service_agreed=True,
            external_account_binding=eab,
        )
        return NewAcctRet(acme_client.new_account(registration), binding, user)

    return wrapped


NewOrderRet = namedtuple("NewOrderRet", ["response", "acme_newacct", "csr"])


@pytest.fixture
def acme_neworder(acme_client: acme.client.ClientV2, acme_newacct):
    def wrapped(
        acme_client=acme_client, new_acct: NewAcctRet = None, cn=None, sans=None
    ):
        if new_acct is None:
            new_acct = acme_newacct()

        csr = helpers.gen_csr(
            cn=cn or "acme.localhost",
            sans=sans or ["acme.localhost", "acme2.localhost"],
        )
        new_order = acme_client.new_order(csr.public_bytes(serialization.Encoding.PEM))
        return NewOrderRet(new_order, new_acct, csr)

    return wrapped


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
