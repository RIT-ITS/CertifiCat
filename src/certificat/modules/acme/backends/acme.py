import datetime

import acme.messages
import josepy
import requests

from cryptography.hazmat.primitives import serialization
from certificat.modules.acme import models as db

from certificat.modules.acme.backends import (
    FinalizeResponse,
    Finalizer,
    StopFinalization,
)
from certificat.settings.dynamic import ACMEFinalizerSettings
from cryptography.hazmat.primitives.asymmetric import rsa
import acme.client
import acme.errors
import logging

logger = logging.getLogger(__name__)


class ACMEFinalizer(Finalizer):
    ca_settings: ACMEFinalizerSettings
    _client: acme.client.ClientV2 | None

    def __init__(self):
        super().__init__()
        self.ca_settings = ACMEFinalizerSettings.get()
        self._client = None

    @property
    def client(self):
        if not self._client:
            try:
                directory = requests.get(self.ca_settings.directory, timeout=5).json()
            except Exception as exc:
                # hide ugly timeout/retry error since these messages are presented to the user
                raise Exception(
                    f"Error reading ACME directory at '{self.ca_settings.directory}'"
                ) from exc

            net = acme.client.ClientNetwork(
                user_agent=self.ca_settings.client_user_agent
            )
            self._client = acme.client.ClientV2(
                acme.client.messages.Directory.from_json(directory), net=net
            )

        return self._client

    def _ensure_account_registered(self):
        binding = db.ACMEFinalizerBinding.get(self.ca_settings.account_kid)
        if binding:
            logger.info("External account binding found, reusing from database.")
            account_key = josepy.JWKRSA.load(binding.private_key.encode())

            account = acme.messages.RegistrationResource.from_json(
                {
                    "body": {
                        "contact": (self.ca_settings.account_email,),
                        "status": "valid",
                        "termsOfServiceAgreed": True,
                    },
                    "uri": binding.account_id,
                }
            )
            self.client.net = acme.client.ClientNetwork(
                account_key, account, user_agent=self.ca_settings.client_user_agent
            )
        else:
            logger.info(
                "External account binding not found, registering with CA from settings."
            )
            # TODO: Make these options configurable
            private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            pem_private_key = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )

            self.client.net.key = josepy.JWKRSA.load(pem_private_key)
            eab = acme.client.messages.ExternalAccountBinding.from_data(
                account_public_key=self.client.net.key.public_key(),
                kid=self.ca_settings.account_kid,
                hmac_key=self.ca_settings.account_hmac_key,
                directory=self.client.directory,
            )

            new_registration = acme.client.messages.NewRegistration.from_data(
                email=self.ca_settings.account_email,
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
                directory=self.client.directory,
                account_id=account_id,
                key_id=self.ca_settings.account_kid,
                private_key=pem_private_key.decode(),
            )

    def finalize(self, order: db.Order, pem_csr: str):
        # This could fail and may retrigger a retry
        self._ensure_account_registered()

        try:
            # This block has automatic retry already built-in, so any exceptions will
            # result in a StopFinalization error that will prevent retry

            new_order = self.client.new_order(pem_csr.encode())

            # This may all be unnecessary. The test server requires answering challenges,
            # other servers may pre-validate the authorizations and skip this step.
            if not self.ca_settings.skip_answering_challenges:
                authz_list = new_order.authorizations
                http_challenges = []
                for authz in authz_list:
                    # Choosing challenge.
                    # authz.body.challenges is a set of ChallengeBody objects.
                    for i in authz.body.challenges:
                        # Find the supported challenge.
                        if isinstance(i.chall, acme.challenges.HTTP01):
                            http_challenges.append(i)

                # This may not be necessary for acme upstreams we integrate with
                for chall in http_challenges:
                    response, _ = chall.response_and_validation(self.client.net.key)
                    # I think there's a bit of a race condition here, the response could say it's been validated
                    # It may be useful to swallow this error or have a toggle to swallow it
                    if not chall.validated:
                        self.client.answer_challenge(chall, response)

            new_order = self.client.poll_and_finalize(
                new_order,
                datetime.datetime.now()
                + datetime.timedelta(seconds=self.ca_settings.finalization_timeout),
            )
            db.Certificate.objects.create(order=order, chain=new_order.fullchain_pem)

            return FinalizeResponse(bundle=new_order.fullchain_pem)
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
            raise StopFinalization(str(exc)) from exc
