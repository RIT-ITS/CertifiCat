import base64
import binascii
import hashlib
import hmac
import json
import typing as t
import uuid
from datetime import timedelta
from math import floor

import acme.messages
import josepy
import requests
from django.utils import timezone

SECRET_PREFIX = "whsec_"
SECRET_MIN_BYTES = 24
SECRET_MAX_BYTES = 64
TIMESTAMP_TOLERANCE = timedelta(minutes=5)
DEFAULT_TIMEOUT = 5


def hmac_data(key: bytes, data: bytes) -> bytes:
    return hmac.new(key, data, hashlib.sha256).digest()


def decode_secret(secret: str) -> bytes:
    """Decodes a Standard Webhooks secret: whsec_ followed by base64."""
    if not secret.startswith(SECRET_PREFIX):
        raise ValueError("Webhook secret must start with 'whsec_'.")
    secret = secret[len(SECRET_PREFIX) :]

    try:
        key = base64.b64decode(secret, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError(
            "Webhook secret must be 'whsec_' followed by base64-encoded bytes."
        ) from exc

    if not SECRET_MIN_BYTES <= len(key) <= SECRET_MAX_BYTES:
        raise ValueError(
            f"Webhook secret must decode to between {SECRET_MIN_BYTES} and "
            f"{SECRET_MAX_BYTES} bytes, got {len(key)}."
        )

    return key


class WebhookVerificationError(Exception):
    pass


class WebhookRequestError(Exception):
    pass


class Webhook:
    """Signs and verifies webhooks according to https://www.standardwebhooks.com/."""

    _key: bytes

    def __init__(self, whsecret: str):
        self._key = decode_secret(whsecret)

    def publish(
        self, endpoint: str, payload: dict, timeout: float = DEFAULT_TIMEOUT
    ) -> requests.Response:
        webhook_id = f"msg_{uuid.uuid4().hex}"
        webhook_timestamp = floor(timezone.now().timestamp())
        webhook_data = json.dumps(payload, separators=(",", ":"))
        signature = self.sign(webhook_id, webhook_timestamp, webhook_data)

        headers = {
            "Content-Type": "application/json",
            "webhook-id": webhook_id,
            "webhook-timestamp": str(webhook_timestamp),
            "webhook-signature": signature,
        }

        response = requests.post(
            endpoint, data=webhook_data, headers=headers, timeout=timeout
        )
        if response.status_code >= 400:
            # try to get JSON error response from server
            try:
                error = response.json().get("error")
            except:  # noqa: E722
                error = "Generic error, no message returned from server."

            raise WebhookRequestError(
                f'Error code {response.status_code} returned from webhook "{endpoint}". Detail: {error}'
            )

        return response

    def verify(self, data: bytes | str, headers: dict[str, str]) -> t.Any:
        data = data if isinstance(data, str) else data.decode()
        headers = {k.lower(): v for (k, v) in headers.items()}
        msg_id = headers.get("webhook-id")
        msg_signature = headers.get("webhook-signature")
        msg_timestamp = headers.get("webhook-timestamp")
        if not (msg_id and msg_timestamp and msg_signature):
            raise WebhookVerificationError("Missing required headers")

        timestamp = self._verify_timestamp(msg_timestamp)

        expected_sig = base64.b64decode(
            self.sign(msg_id=msg_id, timestamp=timestamp, data=data).split(",")[1]
        )
        for versioned_sig in msg_signature.split(" "):
            version, _, signature = versioned_sig.partition(",")
            if version != "v1":
                continue
            try:
                sig_bytes = base64.b64decode(signature)
            except (binascii.Error, ValueError):
                continue
            if hmac.compare_digest(expected_sig, sig_bytes):
                return json.loads(data)

        raise WebhookVerificationError("No matching signature found")

    def sign(self, msg_id: str, timestamp: int, data: str) -> str:
        to_sign = f"{msg_id}.{timestamp}.{data}".encode()
        signature = hmac_data(self._key, to_sign)
        return f"v1,{base64.b64encode(signature).decode('utf-8')}"

    @staticmethod
    def _verify_timestamp(timestamp_header: str) -> int:
        try:
            timestamp = int(timestamp_header)
        except ValueError:
            raise WebhookVerificationError("Invalid Signature Headers")

        now = timezone.now().timestamp()
        if timestamp < now - TIMESTAMP_TOLERANCE.total_seconds():
            raise WebhookVerificationError("Message timestamp too old")
        if timestamp > now + TIMESTAMP_TOLERANCE.total_seconds():
            raise WebhookVerificationError("Message timestamp too new")
        return timestamp


class AuthzWebhookMixin:
    def gather_authorizations(
        self, upstream_order: acme.messages.OrderResource, account_jwk: str
    ):
        authorizations: list = []
        authz_list: list[acme.messages.AuthorizationResource] = (
            upstream_order.authorizations
        )
        for authz in authz_list:
            challenges = []

            challenge_list: list[acme.messages.ChallengeBody] = authz.body.challenges
            for challenge_body in challenge_list:
                if "validation" in challenge_body.chall:
                    challenge = {}
                    challenge["type"] = challenge_body.chall.typ
                    challenge["validation"] = challenge_body.chall.validation(
                        account_jwk
                    )
                    # TODO: Add http-01, but the webhook probably wouldn't do this anyway.
                    # So by not adding it, we're protecting consumers from themself

                    challenges.append(challenge)

            authorizations.append(
                {
                    "id": authz.uri.split("/")[-1],
                    "identifier": f"{authz.body.identifier.typ.name}:{authz.body.identifier.value}",
                    "challenges": challenges,
                }
            )

        return authorizations


class PreAnswerChallengesWebhook(Webhook, AuthzWebhookMixin):
    def publish(
        self,
        endpoint: str,
        account_jwk: josepy.JWK,
        upstream_order: acme.messages.OrderResource,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> requests.Response:

        payload = {
            "type": "order.pre-answer-challenges",
            "timestamp": timezone.now().isoformat(),
            "data": {
                "order": {"id": upstream_order.uri.split("/")[-1]},
                "authorizations": self.gather_authorizations(
                    upstream_order, account_jwk
                ),
            },
        }

        return super().publish(endpoint, payload, timeout=timeout)


class PostAnswerChallengesWebhook(Webhook, AuthzWebhookMixin):
    def publish(
        self,
        endpoint: str,
        account_jwk: josepy.JWK,
        upstream_order: acme.messages.OrderResource,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> requests.Response:
        payload = {
            "type": "order.post-answer-challenges",
            "timestamp": timezone.now().isoformat(),
            "data": {
                "order": {"id": upstream_order.uri.split("/")[-1]},
                "authorizations": self.gather_authorizations(
                    upstream_order, account_jwk
                ),
            },
        }

        return super().publish(endpoint, payload, timeout=timeout)
