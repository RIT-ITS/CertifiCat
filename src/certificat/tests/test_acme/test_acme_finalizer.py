import json
import os
import re
import subprocess
import time
from typing import Callable

from certificat.tests.dns.load_records import Zone
from certificat.tests.dns.server import DNSServer
from certificat.webhooks import Webhook
import requests

from certificat.settings.dynamic import (
    ACMEFinalizerDNS01ChallengeSettings,
    ACMEFinalizerSettings,
    ACMEFinalizerChallengeSettings,
    ApplicationSettings,
    WebhookSettings,
)
from certificat.tests.conftest import NewOrderRet
from certificat.tests.helpers import do_challenge, finalize_order, select_first
import pytest
import acme
from certificat.modules.acme import models as db
import pytest_responses  # noqa: F401
from acme import challenges as acme_challenges
import responses
from acme import errors
from acmev2.models import ChallengeType, OrderStatus


class TestACMEFinalizer:
    responses: responses
    acme_neworder: Callable
    acme_client: acme.client.ClientV2
    acme_acct = None
    pebble_directory = "https://localhost:14000/dir"
    dns_server_port = 11345

    @pytest.fixture(scope="function", autouse=True)
    def setup_test(
        self,
        acme_neworder,
    ):
        self.acme_neworder = acme_neworder
        self.setup_client()

    def setup_client(self):
        client, account, user = self.gen_bound_client()
        self.acme_acct = account
        self.acme_client = client

    @pytest.fixture(scope="function")
    def dns_server(self):
        dns_server = DNSServer(port=self.dns_server_port)
        dns_server.start()

        yield dns_server

        dns_server.stop()

    @pytest.fixture(autouse=True)
    def setup_pebble(self, responses: responses, gen_bound_client):
        self.gen_bound_client = gen_bound_client
        key = "zWNDZM6eQGHWpSRTPal5eIUYFTu7EajVIoguysqZ9wG44nMEtx3MUAsUDkMTQ12W"
        kid = "kid-1"

        ApplicationSettings.get().finalizer = ACMEFinalizerSettings(
            directory=self.pebble_directory,
            account_kid=kid,
            account_hmac_key=key,
            account_email="noreply@acme.edu",
            finalization_timeout=10,
        )

        self.responses = responses

    @pytest.fixture(scope="function")
    def pebble_starter(self):
        responses.add_passthru(re.compile(r"^https?://.*:14000/.*$"))  # pebble

        pebble: subprocess.Popen = None

        def wrapped(requires_eab=True):
            nonlocal pebble
            config = (
                "/opt/pebble/test/config/pebble-config-external-account-bindings.json"
            )
            if not requires_eab:
                config = "/opt/pebble/test/config/pebble-config.json"

            pebble = subprocess.Popen(
                [
                    "/home/vscode/go/bin/pebble",
                    "-config",
                    config,
                ],
                cwd="/opt/pebble",
                env=dict(
                    os.environ,
                    **{
                        "PEBBLE_VA_ALWAYS_VALID": "1",
                        "PEBBLE_VA_NOSLEEP": "1",
                        "PEBBLE_WFE_NONCEREJECT": "0",
                        "PEBBLE_AUTHZREUSE": "100",
                    },
                ),
            )

            timeout = 5
            start_time = time.time()
            # wait for pebble to start
            while True:
                elapsed_time = time.time() - start_time

                if elapsed_time > timeout:
                    raise Exception("Timed out waiting for pebble server to start")

                try:
                    requests.get(self.pebble_directory)
                    break
                except requests.RequestException:
                    pass

                time.sleep(0.1)

            return pebble

        yield wrapped

        if pebble:
            pebble.terminate()
            pebble.wait()

    def _get_processed_order(
        self, expect_failure=False, new_order: NewOrderRet = None
    ) -> db.Order:
        if not new_order:
            new_order: NewOrderRet = self.acme_neworder(
                self.acme_client, self.acme_acct
            )
        order = do_challenge(self.acme_client, new_order.response)

        if expect_failure:
            with pytest.raises(errors.TimeoutError):
                # This always errors, so make it happen fast
                order = finalize_order(self.acme_client, order, timeout=0)
        else:
            order = finalize_order(self.acme_client, order, timeout=5)

        order_name = order.uri.split("/")[-1]
        return db.Order.objects.get(name=order_name)

    @pytest.mark.slow
    @pytest.mark.withoutresponses
    @pytest.mark.django_db
    def test_bind_account(self, pebble_starter):
        pebble_starter()
        # This tests binding the account credentials and getting a certificate
        settings = ACMEFinalizerSettings.get()
        order = self._get_processed_order()
        binding = db.ACMEFinalizerBinding.objects.filter(key_id=settings.account_kid)

        assert len(binding) == 1
        assert order.status == OrderStatus.valid
        assert order.certificate is not None

    @pytest.mark.slow
    @pytest.mark.withoutresponses
    @pytest.mark.django_db
    def test_reuse_account(self, pebble_starter):
        pebble_starter()
        # This tests placing two orders and re-using the account credentials. This should not
        # create another binding.
        settings = ACMEFinalizerSettings.get()
        order = self._get_processed_order()
        binding = db.ACMEFinalizerBinding.objects.filter(key_id=settings.account_kid)

        assert len(binding) == 1
        assert order.status == OrderStatus.valid
        assert order.certificate is not None

        self.setup_client()
        order = self._get_processed_order()
        binding = db.ACMEFinalizerBinding.objects.filter(key_id=settings.account_kid)

        assert len(binding) == 1
        assert order.status == OrderStatus.valid
        assert order.certificate is not None

    @pytest.mark.slow
    @pytest.mark.withoutresponses
    @pytest.mark.django_db
    def test_rebind_account(self, pebble_starter):
        pebble_starter()
        # This tests placing two orders and re-binding the account credentials.
        # With pebble, that works fine. Other ACME servers may not allow rebind.
        settings = ACMEFinalizerSettings.get()
        order = self._get_processed_order()
        binding = db.ACMEFinalizerBinding.objects.filter(key_id=settings.account_kid)

        assert len(binding) == 1
        assert order.status == OrderStatus.valid
        assert order.certificate is not None

        binding.delete()

        self.setup_client()
        order = self._get_processed_order()
        binding = db.ACMEFinalizerBinding.objects.filter(key_id=settings.account_kid)

        assert len(binding) == 1
        assert order.status == OrderStatus.valid
        assert order.certificate is not None

    @pytest.mark.slow
    @pytest.mark.withoutresponses
    @pytest.mark.django_db
    def test_binding_failure(self, pebble_starter):
        pebble_starter()
        # This tests binding with incorrect credentials
        settings = ACMEFinalizerSettings.get()
        settings.account_kid = "invalid-kid"

        order = self._get_processed_order(expect_failure=True)
        binding = db.ACMEFinalizerBinding.objects.filter(key_id=settings.account_kid)

        assert len(binding) == 0
        assert order.status == OrderStatus.invalid
        assert order.last_finalization_error() is not None

    @pytest.mark.slow
    @pytest.mark.withoutresponses
    @pytest.mark.django_db
    def test_server_error(self, pebble_starter):
        pebble = pebble_starter()
        # Tests an order that fails after challenges
        new_order: NewOrderRet = self.acme_neworder(self.acme_client, self.acme_acct)
        order = do_challenge(self.acme_client, new_order.response)

        pebble.terminate()
        pebble.wait()

        try:
            finalize_order(self.acme_client, order, timeout=1)
        except Exception:  # noqa: E722
            pass

        order_name = order.uri.split("/")[-1]
        order = db.Order.objects.get(name=order_name)
        assert order.status == OrderStatus.invalid
        assert order.last_finalization_error() is not None

    @pytest.mark.slow
    @pytest.mark.django_db
    def test_webhooks_called(self, pebble_starter):
        pebble_starter()
        webhook_endpoint = "https://webhook.localhost/pre-neworder"
        shared_secret = "s3cret"
        settings = ACMEFinalizerSettings.get()
        settings.challenges = ACMEFinalizerChallengeSettings(
            challenge_webhook=WebhookSettings(
                secret=shared_secret, endpoint=webhook_endpoint
            )
        )

        verified = False

        def webhook_callback(arg):
            nonlocal verified
            webhook = Webhook(shared_secret)
            webhook.verify(arg.body.encode(), arg.headers)
            verified = True

            return (200, {}, "")

        self.responses.add_callback(
            responses.POST,
            webhook_endpoint,
            callback=webhook_callback,
        )

        new_order: NewOrderRet = self.acme_neworder(self.acme_client, self.acme_acct)
        order = self._get_processed_order()

        assert verified, "Webhook data was not verified"
        assert order.status == OrderStatus.valid
        assert order.certificate is not None

    @pytest.mark.slow
    @pytest.mark.django_db
    def test_webhooks_general_error(self, pebble_starter):
        pebble_starter()
        webhook_endpoint = "https://webhook.localhost/pre-neworder"
        shared_secret = "s3cret"

        settings = ACMEFinalizerSettings.get()
        settings.challenges = ACMEFinalizerChallengeSettings(
            challenge_webhook=WebhookSettings(
                secret=shared_secret, endpoint=webhook_endpoint
            )
        )

        def webhook_callback(arg):
            webhook = Webhook(shared_secret)
            webhook.verify(arg.body.encode(), arg.headers)

            return (500, {}, "")

        self.responses.add_callback(
            responses.POST,
            webhook_endpoint,
            callback=webhook_callback,
        )

        new_order: NewOrderRet = self.acme_neworder(self.acme_client, self.acme_acct)
        order = self._get_processed_order(expect_failure=True)

        assert order.status == OrderStatus.invalid
        assert order.last_finalization_error() is not None

    @pytest.mark.slow
    @pytest.mark.django_db
    def test_webhooks_specific_error(self, pebble_starter):
        pebble_starter()
        webhook_endpoint = "https://webhook.localhost/pre-neworder"
        shared_secret = "s3cret"
        settings = ACMEFinalizerSettings.get()
        settings.challenges = ACMEFinalizerChallengeSettings(
            challenge_webhook=WebhookSettings(
                secret=shared_secret, endpoint=webhook_endpoint
            )
        )

        error_msg = "Error returned from webhook"

        def webhook_callback(arg):
            nonlocal error_msg
            webhook = Webhook(shared_secret)
            webhook.verify(arg.body.encode(), arg.headers)

            return (500, {}, json.dumps({"error": error_msg}))

        self.responses.add_callback(
            responses.POST,
            webhook_endpoint,
            callback=webhook_callback,
        )

        new_order: NewOrderRet = self.acme_neworder(self.acme_client, self.acme_acct)
        order = self._get_processed_order(expect_failure=True)

        assert order.status == OrderStatus.invalid
        assert error_msg in order.last_finalization_error().error

    @pytest.mark.slow
    @pytest.mark.django_db
    def test_check_dns_propagation(self, pebble_starter, dns_server: DNSServer):
        pebble_starter()
        settings = ACMEFinalizerSettings.get()
        settings.challenges = ACMEFinalizerChallengeSettings(
            dns_01=ACMEFinalizerDNS01ChallengeSettings(
                verification_nameservers=[f"127.0.0.1:{self.dns_server_port}"],
                verification_timeout=5,
                perform_verification=True,
            )
        )

        domain = "acme.localhost"
        new_order: NewOrderRet = self.acme_neworder(
            self.acme_client, self.acme_acct, cn=domain, sans=[domain]
        )
        acct_id = self.acme_acct.uri.split("/")[-1]
        account = db.Account.objects.get(name=acct_id)
        authz_resource = new_order.response.authorizations[0]
        dns_chall = select_first(
            authz_resource.body.challenges,
            lambda chall: chall.typ == ChallengeType.dns_01,
        )

        chall_validator = acme_challenges.DNS01(token=dns_chall.token)

        dns_server.add_record(
            Zone(
                f"_acme-challenge.{domain}",
                "TXT",
                chall_validator.validation(account.josepy_jwk()),
            )
        )

        order = self._get_processed_order(new_order=new_order)

        assert order.status == OrderStatus.valid
        assert order.certificate is not None

    @pytest.mark.slow
    @pytest.mark.django_db
    def test_check_dns_propagation_failure(self, pebble_starter, dns_server: DNSServer):
        pebble_starter()
        settings = ACMEFinalizerSettings.get()
        settings.challenges = ACMEFinalizerChallengeSettings(
            dns_01=ACMEFinalizerDNS01ChallengeSettings(
                verification_nameservers=[f"127.0.0.1:{self.dns_server_port}"],
                verification_timeout=1,
                perform_verification=True,
            )
        )

        domain = "acme.localhost"
        new_order: NewOrderRet = self.acme_neworder(
            self.acme_client, self.acme_acct, cn=domain, sans=[domain]
        )

        order = self._get_processed_order(expect_failure=True, new_order=new_order)

        assert order.status == OrderStatus.invalid
        assert order.last_finalization_error() is not None

    @pytest.mark.slow
    @pytest.mark.django_db
    def test_anonymous_account(self, pebble_starter):
        ApplicationSettings.get().finalizer = ACMEFinalizerSettings(
            directory=self.pebble_directory,
            account_email="noreply@acme.edu",
            finalization_timeout=10,
        )

        pebble_starter(requires_eab=False)
        # This tests binding the account credentials and getting a certificate
        settings = ACMEFinalizerSettings.get()
        order = self._get_processed_order()
        binding = db.ACMEFinalizerBinding.objects.filter(key_id=settings.account_kid)

        assert len(binding) == 1
        assert order.status == OrderStatus.valid
        assert order.certificate is not None

    @pytest.mark.slow
    @pytest.mark.withoutresponses
    @pytest.mark.django_db
    def test_reuse_anonymous_account(self, pebble_starter):
        ApplicationSettings.get().finalizer = ACMEFinalizerSettings(
            directory=self.pebble_directory,
            account_email="noreply@acme.edu",
            finalization_timeout=10,
        )

        pebble_starter(requires_eab=False)
        # This tests placing two orders and re-binding the account credentials.
        # With pebble, that works fine. Other ACME servers may not allow rebind.
        settings = ACMEFinalizerSettings.get()
        order = self._get_processed_order()
        binding = db.ACMEFinalizerBinding.objects.filter(key_id=settings.account_kid)

        assert len(binding) == 1
        assert order.status == OrderStatus.valid
        assert order.certificate is not None

        self.setup_client()
        order = self._get_processed_order()
        binding = db.ACMEFinalizerBinding.objects.filter(key_id=settings.account_kid)

        assert len(binding) == 1
        assert order.status == OrderStatus.valid
        assert order.certificate is not None
