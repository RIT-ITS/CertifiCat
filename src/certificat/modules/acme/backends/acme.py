import asyncio
import datetime
import json
import logging
import time

import acme.challenges
import acme.client
import acme.errors
import acme.messages
import dns.exception
import dns.resolver
import josepy
import requests
from acmev2.models.challenge import ChallengeType
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.utils import timezone
from dns.nameserver import Do53Nameserver

from certificat.modules.acme import models as db
from certificat.modules.acme.backends import (
    Finalizer,
    FinalizeResponse,
    StopFinalization,
)
from certificat.modules.acme.util import DNSTXTValidator
from certificat.settings.dynamic import ACMEFinalizerSettings
from certificat.webhooks import PreUpstreamChallengeWebhook

logger = logging.getLogger(__name__)


class ACMEFinalizer(Finalizer):
    settings: ACMEFinalizerSettings
    _client: acme.client.ClientV2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client = None

    @property
    def client(self):
        if not self._client:
            try:
                directory = requests.get(self.settings.directory, timeout=5).json()
            except Exception as exc:
                # hide ugly timeout/retry error since these messages are presented to the user
                raise Exception(  # noqa: TRY002
                    f"Error reading ACME directory at '{self.settings.directory}'"
                ) from exc

            net = acme.client.ClientNetwork(user_agent=self.settings.client_user_agent)
            self._client = acme.client.ClientV2(
                acme.client.messages.Directory.from_json(directory), net=net
            )

        return self._client

    def _ensure_account_registered(self):
        # TODO: Should this also join on directory?
        lookup_args = {"directory": str(self.settings.directory)}
        if self.settings.account_kid:
            lookup_args["key_id"] = self.settings.account_kid
        binding = db.ACMEFinalizerBinding.get(**lookup_args)

        if binding:
            logger.info("Existing account found, reusing from database.")
            account_key = josepy.JWKRSA.load(binding.private_key.encode())

            account = acme.messages.RegistrationResource.from_json(
                {
                    "body": {
                        "contact": (self.settings.account_email,),
                        "status": "valid",
                        "termsOfServiceAgreed": True,
                    },
                    "uri": binding.account_id,
                }
            )
            self.client.net = acme.client.ClientNetwork(
                account_key, account, user_agent=self.settings.client_user_agent
            )
        else:
            logger.info(
                "Existing account not found, registering with CA from settings."
            )
            # TODO: Make these options configurable
            private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            pem_private_key = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )

            self.client.net.key = josepy.JWKRSA.load(pem_private_key)
            if self.settings.account_kid and self.settings.account_hmac_key:
                logger.debug(
                    "EAB settings configured, credentials will be sent with account registration."
                )
                eab = acme.client.messages.ExternalAccountBinding.from_data(
                    account_public_key=self.client.net.key.public_key(),
                    kid=self.settings.account_kid,
                    hmac_key=self.settings.account_hmac_key,
                    directory=self.client.directory,
                )
            else:
                logger.debug("No EAB settings configured, account will be anonymous.")
                eab = None

            new_registration = acme.client.messages.NewRegistration.from_data(
                email=self.settings.account_email,
                terms_of_service_agreed=True,
                external_account_binding=eab,
            )

            account_id: str = None

            try:
                registration = self.client.new_account(new_registration)
                account_id = registration.uri
            except acme.messages.Error as exc:
                raise StopFinalization(
                    f"{exc.typ}: {exc.description} :: {exc.detail}"
                ) from exc
            except acme.errors.ConflictError:
                # This has already been registered. We don't and can't support this.
                raise StopFinalization(
                    "The ACME account has already been bound. Regenerate the ACME EAB credentials and restart the server with new account information."
                )

            db.ACMEFinalizerBinding.objects.create(
                directory=str(self.settings.directory),
                account_id=account_id,
                key_id=self.settings.account_kid,
                private_key=pem_private_key.decode(),
            )

    def execute_challenge_webhook(
        self, upstream_order: acme.messages.OrderResource
    ) -> None:
        webhook_settings = self.settings.challenges.challenge_webhook
        if not webhook_settings:
            return

        logger.info("Executing PreNewOrderWebhook webhook")
        webhook = PreUpstreamChallengeWebhook(webhook_settings.secret)
        webhook.publish(webhook_settings.endpoint, self.client.net.key, upstream_order)

    def check_dns_propagation(
        self, upstream_order: acme.messages.OrderResource
    ) -> bool:
        """Verifies DNS records set for the challenge domains. This never returns False, it raises
        a StopFinalization error on failure.
        """
        verification_tokens: dict[str, str] = {}

        logger.debug("Checking DNS propagation")
        authz_list: list[acme.messages.AuthorizationResource] = (
            upstream_order.authorizations
        )
        for authz in authz_list:
            challenge_list: list[acme.messages.ChallengeBody] = authz.body.challenges
            for challenge_body in challenge_list:
                if challenge_body.get("typ") == ChallengeType.dns_01:
                    verification_tokens[
                        challenge_body.chall.validation_domain_name(
                            authz.body.identifier.value
                        )
                    ] = challenge_body.chall.validation(self.client.net.key)

        timeout = timezone.now() + datetime.timedelta(
            seconds=self.settings.challenges.dns_01.verification_timeout
        )

        # Every resolver must have the record in their cache before we can continue
        resolvers: list[dns.resolver.Resolver] = []
        if self.settings.challenges.dns_01.verification_nameservers:
            for nameserver in self.settings.challenges.dns_01.verification_nameservers:
                logger.info("Creating DNS validator with nameserver: %s", nameserver)
                resolver = dns.resolver.Resolver()
                ip, _, port = nameserver.partition(":")
                resolver.nameservers = [Do53Nameserver(ip, int(port) if port else 53)]

                resolvers.append(resolver)
        else:
            # If a nameserver is not specified (not recommended) then we use a default resolver
            resolvers.append(dns.resolver.Resolver())

        validators = [
            DNSTXTValidator(resolvers, k, v) for k, v in verification_tokens.items()
        ]

        logger.info(
            "Validating the following domains->token pairs: "
            + json.dumps(verification_tokens)
        )

        loop = asyncio.new_event_loop()
        try:
            while timezone.now() < timeout:
                tasks = [
                    loop.create_task(v.validate())
                    for v in validators
                    if not v.validated
                ]
                if len(tasks) == 0:
                    logger.info("All domains verified successfully")
                    return True

                loop.run_until_complete(asyncio.wait(tasks, timeout=15))
                time.sleep(2)
        finally:
            loop.close()

        logger.info("Timeout reached verifying domains.")
        raise StopFinalization("Timeout reached verifying DNS challenges.")

    def preferred_challenge(self):
        if self.settings.challenges.dns_01.perform_verification:
            return acme.challenges.DNS01

        return acme.challenges.HTTP01

    def finalize(self, order: db.Order, pem_csr: str):
        # This could fail and may retrigger a retry
        self._ensure_account_registered()

        try:
            # This block has automatic retry already built-in, so any exceptions will
            # result in a StopFinalization error that will prevent retry

            new_order = self.client.new_order(pem_csr.encode())

            # This may all be unnecessary. The test server requires answering challenges,
            # other servers may pre-validate the authorizations and skip this step.
            if not self.settings.skip_answering_challenges:
                authz_list = new_order.authorizations
                preferred_challenges = []
                for authz in authz_list:
                    # Choosing challenge.
                    # authz.body.challenges is a set of ChallengeBody objects.
                    for i in authz.body.challenges:
                        # Find the preferred/supported challenge.
                        if isinstance(i.chall, self.preferred_challenge()):
                            preferred_challenges.append(i)

                self.execute_challenge_webhook(new_order)
                if self.settings.challenges.dns_01.perform_verification:
                    if not self.check_dns_propagation(new_order):
                        raise StopFinalization("Unable to verify DNS challenges")

                # This may not be necessary for acme upstreams we integrate with
                for chall in preferred_challenges:
                    response, _ = chall.response_and_validation(self.client.net.key)
                    # I think there's a bit of a race condition here, the response could say it's been validated
                    # It may be useful to swallow this error or have a toggle to swallow it
                    if not chall.validated:
                        self.client.answer_challenge(chall, response)

            new_order = self.client.poll_and_finalize(
                new_order,
                datetime.datetime.now()
                + datetime.timedelta(seconds=self.settings.finalization_timeout),
            )
            db.Certificate.objects.create(order=order, chain=new_order.fullchain_pem)

            return FinalizeResponse(bundle=new_order.fullchain_pem)
        except acme.errors.TimeoutError as exc:
            raise StopFinalization(
                "Upstream timed out while finalizing the order"
            ) from exc
        except acme.messages.Error as exc:
            # In the case of an ACME error we stop the execution. The ACME client is already polling, we don't
            # need to restart ACME and retry this order 5-10 times resulting in more failures.
            raise StopFinalization(
                f"{exc.typ}: {exc.description} :: {exc.detail}"
            ) from exc
        except Exception as exc:
            # Same with a generic exception, this isn't a backend that can be retried
            # sanely. We show the full exception because this is a semi-internal service.
            # That may change in the future and we may prompt the user to bring a correlation
            # ID to a server administrator to look at logs.
            raise StopFinalization(
                str(exc) or "No exception given by upstream"
            ) from exc
