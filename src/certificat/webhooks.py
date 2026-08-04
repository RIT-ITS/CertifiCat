import base64
import hashlib
import hmac
import json
import typing as t
from datetime import datetime, timedelta
from math import floor
import uuid
from django.utils import timezone
import josepy
import requests
import acme.messages


def hmac_data(key: bytes, data: bytes) -> bytes:
    return hmac.new(key, data, hashlib.sha256).digest()


class WebhookVerificationError(Exception):
    pass


class WebhookRequestError(Exception):
    pass


class Webhook:
    _whsecret: bytes

    def __init__(self, whsecret: str):
        self._whsecret = whsecret.encode()

    def publish(self, endpoint: str, payload: dict) -> requests.Response:
        webhook_id = f"msg_{uuid.uuid4().hex}"
        webhook_timestamp = timezone.now()
        webhook_data = json.dumps(payload, separators=(",", ":"))
        signature = self.sign(webhook_id, webhook_timestamp, webhook_data)

        headers = {
            "Content-Type": "application/json",
            "webhook-id": webhook_id,
            "webhook-timestamp": str(webhook_timestamp.timestamp()),
            "webhook-signature": signature,
        }

        response = requests.post(endpoint, data=webhook_data, headers=headers)
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

    def verify(self, data: bytes, headers: t.Dict[str, str]) -> t.Any:
        data = data if isinstance(data, str) else data.decode()
        headers = {k.lower(): v for (k, v) in headers.items()}
        msg_id = headers.get("webhook-id")
        msg_signature = headers.get("webhook-signature")
        msg_timestamp = headers.get("webhook-timestamp")
        if not (msg_id and msg_timestamp and msg_signature):
            raise WebhookVerificationError("Missing required headers")

        timestamp = self.__verify_timestamp(msg_timestamp)

        expected_sig = base64.b64decode(
            self.sign(msg_id=msg_id, timestamp=timestamp, data=data).split(",")[1]
        )
        passed_sigs = msg_signature.split(" ")
        for versioned_sig in passed_sigs:
            (version, signature) = versioned_sig.split(",")
            if version != "v1":
                continue
            sig_bytes = base64.b64decode(signature)
            if hmac.compare_digest(expected_sig, sig_bytes):
                return json.loads(data)

        raise WebhookVerificationError("No matching signature found")

    def sign(self, msg_id: str, timestamp: datetime, data: str) -> str:
        timestamp_str = str(floor(timestamp.replace(tzinfo=timezone.UTC).timestamp()))
        to_sign = f"{msg_id}.{timestamp_str}.{data}".encode()
        signature = hmac_data(self._whsecret, to_sign)
        return f"v1,{base64.b64encode(signature).decode('utf-8')}"

    def __verify_timestamp(self, timestamp_header: str) -> datetime:
        webhook_tolerance = timedelta(minutes=5)
        now = datetime.now(tz=timezone.UTC)
        try:
            timestamp = datetime.fromtimestamp(float(timestamp_header), tz=timezone.UTC)
        except Exception:
            raise WebhookVerificationError("Invalid Signature Headers")

        if timestamp < (now - webhook_tolerance):
            raise WebhookVerificationError("Message timestamp too old")
        if timestamp > (now + webhook_tolerance):
            raise WebhookVerificationError("Message timestamp too new")
        return timestamp


class PreUpstreamChallengeWebhook(Webhook):
    def publish(
        self,
        endpoint: str,
        account_jwk: josepy.JWK,
        upstream_order: acme.messages.OrderResource,
    ) -> requests.Response:
        authorizations = []

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

        payload = {
            "type": "order.pre-new",
            "timestamp": timezone.now().isoformat(),
            "data": {
                "order": {"id": upstream_order.uri.split("/")[-1]},
                "authorizations": authorizations,
            },
        }

        return super().publish(endpoint, payload)
