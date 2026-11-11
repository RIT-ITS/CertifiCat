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
    ACMEFinalizerSettings,
    CERTINextACMEFinalizerSettings,
    CERTINextExternalAccountBinding,
)


class CERTINextACMEFinalizer(Finalizer):
    settings: CERTINextACMEFinalizerSettings

    def finalize(self, order: db.Order, pem_csr: str):
        eab_info: CERTINextExternalAccountBinding = self.settings.single_domain_binding
        if order.identifiers.count() > 1:
            eab_info = self.settings.multi_domain_binding

        # Adapt settings to the ACMEFinalizer for reuse
        acme_settings = ACMEFinalizerSettings(
            directory=eab_info.directory,
            account_kid=eab_info.account_kid,
            account_hmac_key=eab_info.account_hmac_key,
            account_email=eab_info.account_email,
            client_user_agent=self.settings.client_user_agent,
        )

        client = create_acme_client(acme_settings)

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
            # Extract preferred challenges from authorizations

            client.answer_preferred_chalenges(new_order)
            new_order = client.poll_and_finalize(
                new_order,
                # The ACME api requires a naive datetime
                datetime.now() + timedelta(seconds=self.settings.finalization_timeout),
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
