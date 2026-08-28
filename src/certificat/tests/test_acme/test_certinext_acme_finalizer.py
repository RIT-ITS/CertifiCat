import json
import os
import subprocess
import time
from collections.abc import Callable
from pathlib import Path

import acme.client
import pytest
import pytest_responses  # noqa: F401
import requests
import responses
from acme import errors
from acmev2.models import OrderStatus

from certificat.modules.acme import models as db
from certificat.settings.dynamic import (
    ApplicationSettings,
    CERTINextACMEFinalizerSettings,
    CERTINextExternalAccountBinding,
)
from certificat.tests.conftest import NewOrderRet
from certificat.tests.helpers import do_challenge, finalize_order

SCRIPT_DIR = Path(__file__).resolve().parent


class TestCERTINextACMEFinalizer:
    """
    This tests ACME finalizer functionality that is specific to the CERTINext ACME Finalizer. Shared functionality
    like binding accounts and creating the ACME client are tested in the more generic ACME Finalizer.
    """

    responses: responses
    acme_neworder: Callable
    acme_client: acme.client.ClientV2
    acme_acct = None

    @pytest.fixture(scope="function", autouse=True)
    def setup_test(self, acme_neworder, gen_bound_client):
        self.acme_neworder = acme_neworder
        client, account, _ = gen_bound_client()
        self.acme_acct = account
        self.acme_client = client

    def setup_finalizer(
        self,
        single_domain_directory: str = "http://localhost:54321/invalid",
        multi_domain_directory: str = "http://localhost:54321/invalid",
    ):
        key = "zWNDZM6eQGHWpSRTPal5eIUYFTu7EajVIoguysqZ9wG44nMEtx3MUAsUDkMTQ12W"
        kid = "kid-1"

        key_multi = "b10lLJs8l1GPIzsLP0s6pMt8O0XVGnfTaCeROxQM0BIt2XrJMDHJZBM5NuQmQJQH"
        kid_multi = "kid-2"

        ApplicationSettings.get().finalizer = CERTINextACMEFinalizerSettings(
            multi_domain_binding=CERTINextExternalAccountBinding(
                directory=multi_domain_directory,
                account_hmac_key=key_multi,
                account_kid=kid_multi,
                account_email="noreply@acme.edu",
            ),
            single_domain_binding=CERTINextExternalAccountBinding(
                directory=single_domain_directory,
                account_hmac_key=key,
                account_kid=kid,
                account_email="noreply@acme.edu",
            ),
        )

    def wrapped_pebble_starter(self, conf="conf/pebble-with-eab.json"):
        config = str(SCRIPT_DIR.joinpath(conf))
        config_contents: dict = json.loads(Path(config).read_text())

        pebble: subprocess.Popen = None

        pebble = subprocess.Popen(
            [
                "/home/vscode/go/bin/pebble",
                "-config",
                config,
            ],
            cwd="/opt/pebble",
            env=dict(
                os.environ,
                PEBBLE_VA_ALWAYS_VALID="1",
                PEBBLE_VA_NOSLEEP="1",
                PEBBLE_WFE_NONCEREJECT="0",
                PEBBLE_AUTHZREUSE="100",
            ),
        )

        directory = f"https://localhost:{config_contents['pebble']['listenAddress'].split(':')[1]}/dir"
        timeout = 5
        start_time = time.time()
        # wait for pebble to start
        while True:
            elapsed_time = time.time() - start_time

            if elapsed_time > timeout:
                raise Exception("Timed out waiting for pebble server to start")  # noqa: TRY002

            try:
                requests.get(directory)
                break
            except requests.RequestException as exc:
                print(exc)

            time.sleep(0.1)

        return pebble, directory

    @pytest.fixture(scope="function")
    def single_domain_directory(self):
        pebble: subprocess.Popen = None

        pebble, directory = self.wrapped_pebble_starter()

        yield directory

        if pebble:
            pebble.terminate()
            pebble.wait()

    @pytest.fixture(scope="function")
    def multi_domain_directory(self):
        pebble: subprocess.Popen = None

        pebble, directory = self.wrapped_pebble_starter(
            conf="conf/pebble-with-eab-port-14001.json"
        )

        yield directory

        if pebble:
            pebble.terminate()
            pebble.wait()

    def _get_processed_order(
        self,
        expect_failure=False,
        new_order: NewOrderRet = None,
        sans: list[str] | None = None,
        timeout=5,
    ) -> db.Order:
        if not new_order:
            new_order: NewOrderRet = self.acme_neworder(
                self.acme_client, self.acme_acct, sans=sans
            )
        order = do_challenge(self.acme_client, new_order.response)

        if expect_failure:
            with pytest.raises(errors.TimeoutError):
                # This always errors, so make it happen fast
                order = finalize_order(self.acme_client, order, timeout=0)
        else:
            order = finalize_order(self.acme_client, order, timeout=timeout)

        order_name = order.uri.split("/")[-1]
        return db.Order.objects.get(name=order_name)

    @pytest.mark.slow
    @pytest.mark.withoutresponses
    @pytest.mark.django_db
    def test_single_domain_cert(self, single_domain_directory: str):
        # This tests binding the account credentials and getting a certificate with a single domain
        # It's meant to ensure the correct code path is taken

        # The second part of the test tries to finalize a multi-domain cert and that fails
        # excpectedly because that binding is set to a service that doesn't exist

        self.setup_finalizer(single_domain_directory=single_domain_directory)
        settings = CERTINextACMEFinalizerSettings.get()
        order = self._get_processed_order(sans=["acme.localhost"])
        binding = db.ACMEFinalizerBinding.objects.filter(
            key_id=settings.single_domain_binding.account_kid
        )

        assert len(binding) == 1
        assert order.status == OrderStatus.valid
        assert order.certificate is not None

        order = self._get_processed_order(
            sans=["acme.localhost", "acme2.localhost"], expect_failure=True
        )
        binding = db.ACMEFinalizerBinding.objects.filter(
            key_id=settings.multi_domain_binding.account_kid
        )

        assert len(binding) == 0
        assert order.status == OrderStatus.invalid

    @pytest.mark.slow
    @pytest.mark.withoutresponses
    @pytest.mark.django_db
    def test_multi_domain_cert(self, multi_domain_directory: str):
        # This tests binding the account credentials and getting a certificate with multiple domains
        # It's meant to ensure the correct code path is taken

        # The second part of the test tries to finalize a single-domain cert and that fails
        # excpectedly because that binding is set to a service that doesn't exist

        # This is the inverse to the snigle domain cert test

        self.setup_finalizer(multi_domain_directory=multi_domain_directory)
        settings = CERTINextACMEFinalizerSettings.get()
        order = self._get_processed_order(sans=["acme.localhost", "acme2.localhost"])
        binding = db.ACMEFinalizerBinding.objects.filter(
            key_id=settings.multi_domain_binding.account_kid
        )

        assert len(binding) == 1
        assert order.status == OrderStatus.valid
        assert order.certificate is not None

        order = self._get_processed_order(sans=["acme.localhost"], expect_failure=True)
        binding = db.ACMEFinalizerBinding.objects.filter(
            key_id=settings.single_domain_binding.account_kid
        )

        assert len(binding) == 0
        assert order.status == OrderStatus.invalid

    @pytest.mark.slow
    @pytest.mark.withoutresponses
    @pytest.mark.django_db
    def test_server_error(self):
        pebble, directory = self.wrapped_pebble_starter()
        self.setup_finalizer(single_domain_directory=directory)
        # Tests an order that fails after challenges

        new_order: NewOrderRet = self.acme_neworder(
            self.acme_client, self.acme_acct, sans=["acme.localhost"]
        )
        order = do_challenge(self.acme_client, new_order.response)

        pebble.terminate()
        pebble.wait()

        try:
            finalize_order(self.acme_client, order, timeout=1)
        except Exception:  # noqa: BLE001, S110
            pass

        order_name = order.uri.split("/")[-1]
        order = db.Order.objects.get(name=order_name)
        assert order.status == OrderStatus.invalid
        assert order.last_finalization_error() is not None
