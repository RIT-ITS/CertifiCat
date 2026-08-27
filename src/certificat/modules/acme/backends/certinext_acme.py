from datetime import datetime, timedelta

import acme.challenges
import acme.errors
import acme.messages

from certificat.modules.acme import models as db
from certificat.modules.acme.backends import (
    Finalizer,
    FinalizeResponse,
    StopFinalization,
)
from certificat.modules.acme.backends.acme import (
    create_acme_client,
    ensure_acme_account_registered,
)
from certificat.settings.dynamic import (
    CERTINextACMEFinalizerSettings,
    CERTINextExternalAccountBinding,
)


class CERTINextACMEFinalizer(Finalizer):
    settings: CERTINextACMEFinalizerSettings

    def finalize(self, order: db.Order, pem_csr: str):
        eab_info: CERTINextExternalAccountBinding = self.settings.single_domain_binding
        if order.identifiers.count() > 1:
            eab_info = self.settings.multi_domain_binding

        client = create_acme_client(eab_info.directory, self.settings.client_user_agent)
        # This could fail and may retrigger a retry
        ensure_acme_account_registered(
            client,
            eab_info.account_email,
            eab_info.account_kid,
            eab_info.account_hmac_key,
        )

        try:
            # This block has automatic retry already built-in, so any exceptions will
            # result in a StopFinalization error that will prevent retry

            new_order = client.new_order(pem_csr.encode())

            # Extract authorizations
            authz_list: list[acme.messages.AuthorizationResource] = (
                new_order.authorizations
            )

            # Extract preferred challenges from authorizations
            preferred_challenges: list[acme.messages.ChallengeBody] = []
            for authz in authz_list:
                # Choosing challenge.
                challenges: list[acme.messages.ChallengeBody] = authz.body.challenges
                for c in challenges:
                    # Find the preferred/supported challenge.
                    if isinstance(c.chall, acme.challenges.HTTP01):
                        preferred_challenges.append(c)

            # This is likely only necessary for the test ACME client, we can't answer
            # http-01 challenges from CERTInext, but this is needed to satisfy Pebble
            for chall in preferred_challenges:
                response, _ = chall.response_and_validation(client.net.key)
                # I think there's a bit of a race condition here, the response could say it's been validated
                # It may be useful to swallow this error or have a toggle to swallow it
                if not chall.validated:
                    # again, this code should never get called in production because
                    # everything should be validated
                    client.answer_challenge(chall, response)

            new_order = client.poll_and_finalize(
                new_order,
                # The ACME api requires a naive datetime
                datetime.now() + timedelta(seconds=self.settings.finalization_timeout),  # noqa: DTZ005
            )
            db.Certificate.objects.create(order=order, chain=new_order.fullchain_pem)

            return FinalizeResponse(bundle=new_order.fullchain_pem)
        except acme.errors.TimeoutError as exc:
            raise StopFinalization(
                "CERTINext timed out while finalizing the order."
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
                str(exc)
                or "No exception given by CERTINext, more information may be available in the logs."
            ) from exc
