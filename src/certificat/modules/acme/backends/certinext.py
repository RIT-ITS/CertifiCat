import logging

import certinext as cn
from certinext.ssl_certificates import OrderWorkflow

from certificat.modules.acme.backends import (
    FinalizeResponse,
    Finalizer,
    NotReadyException,
)
from certificat.modules.acme import models as db
from certificat.settings.dynamic import CertinextSettings

logger = logging.getLogger(__name__)


class CertinextFinalizer(Finalizer):
    """Finalizer that issues certificates via the CertiNext CA.

    Delegates the full certificate lifecycle to the ``certinext`` library.
    Persists the CertiNext order ID in :class:`~certificat.modules.acme.models.CertinextOrderRef`
    so that the Huey task retries never create a duplicate order — each retry
    re-derives the live order status from the CertiNext API and advances it one step.

    Configuration is read from the ``certinext_finalizer`` section of the
    CertifiCat config file via :class:`~certificat.settings.dynamic.CertinextSettings`.
    """

    def _build_session(self, s: CertinextSettings) -> cn.CertiNextSession:
        """Build and return an authenticated CertiNext session.

        Extracted as a method so tests can override it without touching the
        live API.

        Args:
            s: Validated CertiNext settings.

        Returns:
            A configured :class:`certinext.CertiNextSession`.
        """
        base_url = s.base_url or (cn.SANDBOX_BASE_URL if s.sandbox else cn.BASE_URL)
        token_url = s.token_url or (
            cn.SANDBOX_TOKEN_URL if s.sandbox else cn.TOKEN_URL
        )
        return cn.session(
            base_url=base_url,
            token_url=token_url,
            client_id=s.client_id,
            client_secret=s.client_secret,
            scope=s.scope,
            sandbox=s.sandbox,
        )

    def finalize(self, order: db.Order, pem_csr: str) -> FinalizeResponse:
        """Drive a CertiNext SSL order to issuance and return the PEM chain.

        On the first call, creates a new CertiNext order and persists its ID.
        On subsequent calls (Huey retries), resumes from the persisted ID.
        Each call advances the order one step via :meth:`OrderWorkflow.advance`.

        Raises :exc:`~certificat.modules.acme.backends.NotReadyException` when
        the order is still in progress (triggering a Huey retry). Raises a plain
        :exc:`Exception` for terminal failures or unexpected states (triggering an
        :class:`~certificat.modules.acme.models.OrderFinalizationError` and a retry).

        Args:
            order: The CertifiCat order being finalized.
            pem_csr: PEM-encoded Certificate Signing Request.

        Returns:
            :class:`~certificat.modules.acme.backends.FinalizeResponse` with the
            leaf-first PEM fullchain on success.

        Raises:
            NotReadyException: When the CertiNext order is still processing.
            Exception: On terminal failures or unexpected DCV requirements.
        """
        log_prefix = f"order {order.name}"
        s = CertinextSettings.get()
        sess = self._build_session(s)

        ref = db.CertinextOrderRef.for_order(order)

        # Collect the ACME-authoritative domain list from the order identifiers.
        domains = [i.value for i in order.identifiers.all()]
        primary_domain = domains[0] if domains else ""
        additional_domains = domains[1:] if len(domains) > 1 else []

        # Resolve the requestor email: config override takes precedence, then
        # fall back to the account binding email (same logic as SectigoFinalizer).
        if s.requestor_email:
            requestor_email = s.requestor_email
        elif order.account.binding:
            requestor_email = order.account.binding.creator.email
        else:
            requestor_email = ""

        if ref.certinext_order_id is None:
            logger.info(f"{log_prefix}: creating CertiNext order for {primary_domain!r}")
            ssl_order = sess.ssl.create(
                s.product,
                primary_domain,
                organization_id=s.organization_id,
                additional_domains=additional_domains or None,
                csr=pem_csr.strip(),
                validity_years=s.validity_years,
                requestor_name=s.requestor_name,
                requestor_email=requestor_email,
                requestor_phone=s.requestor_phone,
                requestor_designation=s.requestor_designation,
                signer_name=s.signer_name,
                signer_place=s.signer_place,
                prevetting_token=s.prevetting_token or None,
            )
            # Persist the order ID before doing anything else so a retry never
            # re-creates the order even if the task is killed immediately after.
            ref.certinext_order_id = ssl_order.order_id
            ref.save()
            logger.info(f"{log_prefix}: CertiNext order {ssl_order.order_id!r} created")
            wf = OrderWorkflow(
                ssl_order,
                signer_name=s.signer_name,
                signer_place=s.signer_place,
                auto_verify_dcv=False,
            )
        else:
            logger.info(
                f"{log_prefix}: resuming CertiNext order {ref.certinext_order_id!r}"
            )
            wf = OrderWorkflow.from_order_id(
                sess,
                ref.certinext_order_id,
                signer_name=s.signer_name,
                signer_place=s.signer_place,
                auto_verify_dcv=False,
            )

        wf.advance(pem_csr)
        status = wf.status

        if wf.is_complete:
            logger.info(f"{log_prefix}: CertiNext order {ref.certinext_order_id!r} issued")
            chain = wf.download_chain()
            db.Certificate.objects.create(order=order, chain=chain)
            return FinalizeResponse(bundle=chain)

        if status == "pending-dcv":
            # UMS domains are pre-validated in CertiNext and ACME has already
            # proven domain control — DCV here signals a misconfiguration.
            raise Exception(
                f"CertiNext order {ref.certinext_order_id!r} requires DCV "
                "(pending-dcv); UMS domains should be pre-validated"
            )

        if wf.is_terminal:
            raise Exception(
                f"CertiNext order {ref.certinext_order_id!r} ended in terminal "
                f"status {status!r}"
            )

        # Order is still in a pending state (pending-approval, pending-csr,
        # pending-agreement, etc.) — signal the task runner to retry.
        logger.info(
            f"{log_prefix}: CertiNext order {ref.certinext_order_id!r} status={status!r}, "
            "will retry"
        )
        raise NotReadyException()
