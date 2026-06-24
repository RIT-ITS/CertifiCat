from datetime import datetime
import time

from certificat.modules.acme import models as db

from certificat.modules.acme.backends import (
    FinalizeResponse,
    Finalizer,
    StopFinalization,
)
from certificat.settings.dynamic import ApplicationSettings, CertiNextFinalizerSettings
import inject
from .backend import CertiNextBackend
import logging

logger = logging.getLogger(__name__)


class CertiNextFinalizer(Finalizer):
    # These states fail the order straight away
    invalid_order_states = ["cancelled", "revoked", "expired"]

    # This means the order is ready to be moved to the next stage
    finished_order_states = ["issued"]

    # These states fail the certificate right away
    invalid_certificate_states = [
        2,  # Pending for Approver
        3,  # Under Discrepancy
        5,  # Rejected
        6,  # Pending Second Approver
        8,  # Rejected by Second Approver
        9,  # Certificate Downloaded
        12,  # Certificate Expired
        13,  # Rejected due to Order Cancellation
        14,  # Auto Rejected
        16,  # Pending LRA
        18,  # Rejected LRA
        19,  # Invalid Configuration
        21,  # Download Rejected
        22,  # Certificate Revoked
        24,  # Pending for Approver (Auto-approval)
        25,  # Organization Authorization Pending LRA
        27,  # Organization Authorization Rejected LRA
    ]

    # This means the order is ready to be moved to the next stage
    finished_certificate_states = [
        20,  # Certificate Generated
    ]

    def __init__(self):
        self.backend = CertiNextBackend()

    def finalize(self, order: db.Order, pem_csr: str):
        ca_settings: CertiNextFinalizerSettings = inject.instance(
            ApplicationSettings
        ).finalizer
        log_prefix = "order " + order.name

        # The latest state of the order. Orders go from
        # Submitted -> Ordered -> Fulfilled and can fail at any
        # point in the process.
        processing_state: db.CertiNextOrderProcessingState = (
            db.CertiNextOrderProcessingState.for_order(order)
        )

        # Client has submitted an order to CertifiCat
        if processing_state.state == db.CertiNextOrderProcessingState.Choices.SUBMITTED:
            logger.info(f"{log_prefix}: generating upstream order")

            gen_order_response = self.backend.generate_order(order, pem_csr)
            if gen_order_response.is_error():
                raise StopFinalization(
                    "Error submitting order: " + gen_order_response.error.description
                )

            if gen_order_response.wrapped.status in self.invalid_order_states:
                raise StopFinalization(
                    "Order in invalid state: " + gen_order_response.wrapped.status
                )

            processing_state.order_number = gen_order_response.wrapped.order_number
            logger.info(f"{log_prefix}: order successfully generated")
            processing_state.transition_to(
                db.CertiNextOrderProcessingState.Choices.ORDERED
            )

        # CertifiCat has submitted the order to CERTINext
        if processing_state.state == db.CertiNextOrderProcessingState.Choices.ORDERED:
            start = datetime.now()
            while (
                processing_state.state
                != db.CertiNextOrderProcessingState.Choices.FULFILLED
            ):
                logger.info(f"{log_prefix}: polling for fulfillment")
                track_order_response = self.backend.track_order(
                    processing_state.order_number
                )
                if track_order_response.is_error():
                    raise StopFinalization(
                        "Error tracking order: "
                        + track_order_response.error.description
                    )

                if track_order_response.wrapped.status in self.invalid_order_states:
                    raise StopFinalization(
                        "Order in invalid state: " + track_order_response.wrapped.status
                    )

                if track_order_response.wrapped.status in self.finished_order_states:
                    logger.info(f"{log_prefix}: order fulfilled")
                    processing_state.transition_to(
                        db.CertiNextOrderProcessingState.Choices.FULFILLED
                    )

                if (
                    processing_state.state
                    != db.CertiNextOrderProcessingState.Choices.FULFILLED
                ):
                    if (datetime.now() - start).seconds >= ca_settings.poll_deadline:
                        raise StopFinalization(
                            f"{log_prefix}: polling deadline exceeded"
                        )
                    time.sleep(ca_settings.poll_interval)

        if processing_state.state == db.CertiNextOrderProcessingState.Choices.FULFILLED:
            logger.info(f"{log_prefix}: downloading certificate")
            cert_response = self.backend.get_certificate(processing_state.order_number)
            if cert_response.is_error():
                raise StopFinalization(
                    "Error downloading certificate: " + cert_response.error.description
                )

            logger.info(f"{log_prefix}: certificate downloaded")
            # Certs are stored in client -> intermediate(s) -> root order
            chain = cert_response.wrapped.cert

            # Some clients (like certbot) expect the bundle to end with a newline and will
            # fail if it doesn't.
            if not chain.endswith("\n"):
                chain += "\n"

            db.Certificate.objects.create(order=order, chain=chain)
            processing_state.transition_to(
                db.SectigoOrderProcessingState.Choices.COLLECTED
            )

        if processing_state.state == db.SectigoOrderProcessingState.Choices.COLLECTED:
            return FinalizeResponse(
                bundle=db.Certificate.objects.get(order=order).chain
            )
