from certificat.settings.dynamic import ApplicationSettings
from certificat.webhooks import PreUpstreamChallengeWebhook
import inject
import pytest
from django.test import Client
from acmev2.settings import ACMESettings, Challenges
import responses
from ..helpers import create_cert
from certificat.modules.acme import models as db


class TestWebhooks:
    @pytest.fixture(autouse=True)
    def setup_class_members(self, gen_bound_client):
        self.gen_bound_client = gen_bound_client
        client, account, user = self.gen_bound_client()

        self.client = client
        self.acme_user = user

    def create_order(self):
        settings = inject.instance(ApplicationSettings)
        settings.finalizer.type = "local"

        return create_cert(self.client, "test.localhost", ["test.localhost"])

    @pytest.mark.django_db
    def test_pre_neworder_webhook(self, web_client: Client, responses: responses):
        local_acme_settings = inject.instance(ACMESettings)
        local_acme_settings.challenges_available = [
            Challenges.http_01,
            Challenges.dns_01,
        ]
        order_resource = self.create_order()
        order = db.Order.objects.get(name=order_resource.id)
        secret = "s*cret"
        webhook = PreUpstreamChallengeWebhook(secret)

        webhook_endpoint = "https://webhook.localhost/pre-neworder"

        # Test that signature verifies
        verified = False

        def webhook_callback(arg):
            nonlocal verified
            webhook = PreUpstreamChallengeWebhook(secret)
            verified = webhook.verify(arg.body.encode(), arg.headers) is not None

            # reflect the body back, this doesn't have to happen
            return (200, {}, arg.body)

        responses.add_callback(
            responses.POST,
            webhook_endpoint,
            callback=webhook_callback,
        )

        resp = webhook.publish(webhook_endpoint, order)
        challenges = resp.json()["data"]["authorizations"][0]["challenges"]

        assert verified
        # Two challenges are sent, one http-01 and one dns-01
        assert len(challenges) == 2
        # Only dns-01 has the validation key
        assert len([c for c in challenges if "validation" in c]) == 1
