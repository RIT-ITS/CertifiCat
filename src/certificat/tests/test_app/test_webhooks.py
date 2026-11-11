import base64
import time
from unittest import mock

import acme.client
import inject
import pytest
import responses
from acmev2.settings import Challenges
from django.test import Client
from pydantic import ValidationError

from certificat.modules.acme import models as db
from certificat.settings.dynamic import LocalACMESettings, WebhookSettings
from certificat.webhooks import (
    PreAnswerChallengesWebhook,
    Webhook,
    WebhookVerificationError,
    decode_secret,
)


class TestWebhooks:
    @pytest.fixture(autouse=True)
    def setup_class_members(self, gen_bound_client):
        self.gen_bound_client = gen_bound_client
        client, account, user = self.gen_bound_client()

        self.client = client
        self.acme_user = user

    @pytest.mark.django_db
    def test_pre_neworder_webhook(
        self,
        web_client: Client,
        responses: responses,
        acme_client: acme.client.ClientV2,
        acme_neworder,
    ):
        local_acme_settings = inject.instance(LocalACMESettings)
        local_acme_settings.challenges_available = [
            Challenges.http_01,
            Challenges.dns_01,
        ]

        new_order = acme_neworder()

        order = db.Order.objects.get(name=new_order.response.uri.split("/")[-1])
        secret = "whsec_MfKQ9r8GKYqrTwjUPD8ILPZIo2LaLaSw"
        webhook = PreAnswerChallengesWebhook(secret)

        webhook_endpoint = "https://webhook.localhost/pre-neworder"

        # Test that signature verifies
        verified = False

        def webhook_callback(arg):
            nonlocal verified
            webhook = PreAnswerChallengesWebhook(secret)
            verified = webhook.verify(arg.body.encode(), arg.headers) is not None

            # reflect the body back, this doesn't have to happen
            return (200, {}, arg.body)

        responses.add_callback(
            responses.POST,
            webhook_endpoint,
            callback=webhook_callback,
        )

        resp = webhook.publish(
            webhook_endpoint, acme_client.net.key, new_order.response
        )
        challenges = resp.json()["data"]["authorizations"][0]["challenges"]

        assert verified
        # Two challenges are sent, one http-01 and one dns-01
        assert len(challenges) == 2
        # Both have the validation key
        assert len([c for c in challenges if "validation" in c]) == 2


SPEC_SECRET = "whsec_MfKQ9r8GKYqrTwjUPD8ILPZIo2LaLaSw"


class TestWebhookSigning:
    def test_matches_standard_webhooks_vector(self):
        # Test vector from the Standard Webhooks reference implementations
        webhook = Webhook(SPEC_SECRET)
        signature = webhook.sign(
            "msg_p5jXN8AQM9LWM0D4loKWxJek", 1614265330, '{"test": 2432232314}'
        )
        assert signature == "v1,g0hM9SsE+OTPJTGt/tmIKtSyZlE3uFJELVlNIOLJ1OE="

    def test_secret_prefix_is_required(self):
        unprefixed = SPEC_SECRET.removeprefix("whsec_")
        with pytest.raises(ValueError):
            decode_secret(unprefixed)

    @pytest.mark.parametrize(
        "secret",
        [
            "s3cret",  # not base64
            "whsec_" + base64.b64encode(b"x" * 23).decode(),  # too short
            "whsec_" + base64.b64encode(b"x" * 65).decode(),  # too long
        ],
    )
    def test_invalid_secrets_rejected(self, secret):
        with pytest.raises(ValueError):
            decode_secret(secret)
        with pytest.raises(ValidationError):
            WebhookSettings(secret=secret, endpoint="https://webhook.localhost/")

    def test_publish_headers_and_timeout(self):
        webhook = Webhook(SPEC_SECRET)
        with mock.patch("certificat.webhooks.requests.post") as post:
            post.return_value.status_code = 204
            webhook.publish("https://webhook.localhost/", {"a": 1}, timeout=7)

        _, kwargs = post.call_args
        assert kwargs["timeout"] == 7
        headers = kwargs["headers"]
        # Standard Webhooks requires integer seconds
        assert headers["webhook-timestamp"].isdigit()
        assert webhook.verify(kwargs["data"], headers) == {"a": 1}

    def test_verify_rejects_old_timestamp(self):
        webhook = Webhook(SPEC_SECRET)
        old = int(time.time()) - 600
        body = '{"a":1}'
        headers = {
            "webhook-id": "msg_1",
            "webhook-timestamp": str(old),
            "webhook-signature": webhook.sign("msg_1", old, body),
        }
        with pytest.raises(WebhookVerificationError):
            webhook.verify(body, headers)
