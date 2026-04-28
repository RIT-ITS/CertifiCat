import os
import subprocess
import time
from typing import Callable

import requests

from certificat.settings.dynamic import (
    ACMEFinalizerSettings,
    ApplicationSettings,
)
from certificat.tests.conftest import NewOrderRet
from certificat.tests.helpers import do_challenge, finalize_order
import pytest
import acme
from certificat.modules.acme import models as db
import pytest_responses  # noqa: F401
import responses
from acme import errors
from acmev2.models import OrderStatus


class TestACMEFinalizer:
    responses: responses
    acme_neworder: Callable
    acme_client: acme.client.ClientV2
    acme_acct = None
    pebble_directory = "https://localhost:14000/dir"

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

    @pytest.fixture(scope="class")
    def pebble_process(self):
        pebble = subprocess.Popen(
            [
                "/home/vscode/go/bin/pebble",
                "-config",
                "/opt/pebble/test/config/pebble-config-external-account-bindings.json",
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

        yield pebble

        pebble.terminate()
        pebble.wait()

    def _get_processed_order(self, expect_failure=False) -> db.Order:
        new_order: NewOrderRet = self.acme_neworder(self.acme_client, self.acme_acct)
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
    def test_bind_account(self, pebble_process):
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
    def test_reuse_account(self, pebble_process):
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
    def test_rebind_account(self, pebble_process):
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
    def test_binding_failure(self, pebble_process):
        # This tests binding with incorrect credentials
        # With pebble, that works fine. Other ACME servers may not allow rebind.
        settings = ACMEFinalizerSettings.get()
        settings.account_kid = "invalid-kid"

        order = self._get_processed_order(expect_failure=True)
        binding = db.ACMEFinalizerBinding.objects.filter(key_id=settings.account_kid)

        assert len(binding) == 0
        assert order.status == OrderStatus.invalid
        assert order.last_finalization_error is not None
