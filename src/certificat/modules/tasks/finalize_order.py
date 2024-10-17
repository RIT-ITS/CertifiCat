from datetime import datetime
import logging
import time

from certificat.modules.acme.backends import Backend
from huey.contrib.djhuey import HUEY
from certificat.modules.acme import models as db
from acmev2.models import OrderStatus
from certificat.settings.dynamic import ApplicationSettings
import inject
from django.utils.module_loading import import_string

logger = logging.getLogger(__name__)


def _run_task(order_name: str):
    app_settings = inject.instance(ApplicationSettings)
    log_prefix = "order " + order_name
    order = db.Order.objects.get(name=order_name)
    if order.status != OrderStatus.processing:
        logger.info(f"{log_prefix}: order in invalid state {order.status}")

    csr = db.CertificateRequest.objects.get(order=order).csr
    # csr = load_pem_x509_csr(csr_bytes)

    # start!
    logger.info(f"{log_prefix}: creating backend")
    # Create a module path (everything before the last dot) and get the
    # className (the last path item) from that module.
    backend_klass = import_string(app_settings.ca_module)
    backend: Backend = backend_klass()

    processing_state: db.OrderProcessingState = db.OrderProcessingState.for_order(order)

    if processing_state.state == db.OrderProcessingState.Choices.SUBMITTED:
        logger.info(f"{log_prefix}: enrolling csr")
        # Enroll the certificate. This kicks off a process and the CA has to issue a new certificate
        # and either auto-approve it or ask the user to approve it.
        enroll_response = backend.enroll(csr)
        processing_state.ssl_id = enroll_response.ssl_id
        processing_state.save()

        if not enroll_response.ok():
            raise Exception(
                f"Error {enroll_response.error.code}: {enroll_response.error.description}"
            )

        processing_state.transition_to(db.OrderProcessingState.Choices.ENROLLED)

    if processing_state.state == db.OrderProcessingState.Choices.ENROLLED:
        ready_for_approval = False
        approved = False
        # Poll the certificate endpoint every few seconds to see if it's ready for approval. It may also
        # be auto-approved depending on the rules set up for the org/department.
        start = datetime.now()
        while not (ready_for_approval or approved):
            logger.info(f"{log_prefix}: polling for approval")
            get_response = backend.get(processing_state.ssl_id)
            if not get_response.ok():
                raise Exception(
                    f"Error {get_response.error.code}: {get_response.error.description}"
                )

            ready_for_approval = get_response.cert_status == "requested"
            approved = get_response.approved is not None

            if (datetime.now() - start).seconds > backend.poll_deadline:
                raise Exception(
                    "Polling deadline exceeded for state " + processing_state.state
                )

            if not (ready_for_approval or approved):
                time.sleep(1)

        # If the certificate isn't approved we need to make a final call to approve it.
        if not approved:
            logger.info(f"{log_prefix}: approving certificate")
            approve_response = backend.approve(
                processing_state.ssl_id, message="Auto-approved by ACME"
            )
            if not approve_response.ok():
                raise Exception(
                    f"Error {approve_response.error.code}: {approve_response.error.description}"
                )

            approved = True

        processing_state.transition_to(db.OrderProcessingState.Choices.APPROVED)

    if processing_state.state == db.OrderProcessingState.Choices.APPROVED:
        logger.info("collecting certificate")
        # Get the certificate PEM bundle

        collect_response = backend.collect(processing_state.ssl_id)
        if not collect_response.ok():
            raise Exception(
                f"Error {collect_response.error.code}: {collect_response.error.description}"
            )

        # Some clients (like certbot) expect the bundle to end with a newline and will
        # fail if it doesn't.
        if not collect_response.bundle.endswith("\n"):
            collect_response.bundle += "\n"

        db.Certificate.objects.create(order=order, chain=collect_response.bundle)

        processing_state.transition_to(db.OrderProcessingState.Choices.COLLECTED)

    order.status = OrderStatus.valid
    order.save()

    return True


def finalize_order_task(order_name: str, task=None):
    lock_key = f"final-{order_name}"
    log_prefix = "order " + order_name

    if HUEY.is_locked(lock_key):
        logger.info(f"{log_prefix}: exiting task, lock not acquired for {lock_key}")
        return

    with HUEY.lock_task(lock_key):
        passed = False
        try:
            passed = _run_task(order_name)
            # If it runs through
        except Exception:
            logger.exception("error in order finalization")

        if not passed and task.retries == 0 or HUEY.immediate:
            logger.info(f"{log_prefix}: retries exceeded, marking order and invalid")
            order_service.update_status(order, OrderStatus.invalid)

        # certs = load_certificates(collect_response.bundle.encode())

        # HACK: the certs are not in the correct order and the api documentation
        # doesn't match what it should be. It should be our cert, then any intermediates, then the root,
        # instead it is the root, intermediates, then our requested cert.
        # We'll just reverse the chain for now, hopefully they don't fix the api underneath us.
        # certs.reverse()
        # final_pem_bundle = ""
        # for cert in certs:
        #    final_pem_bundle += dump_certificate(FILETYPE_PEM, cert).decode()

        # cert_raw = base64.b64encode(dump_certificate(FILETYPE_ASN1, certs[0])).decode()

        # (issue_uts, expire_uts) = cert_dates_get(logger, cert_raw)

        # cert_record = Certificate.objects.get(order=order)
        # cert_record.cert_raw = cert_raw
        # cert_record.cert = final_pem_bundle
        # cert_record.expire_uts = expire_uts
        # cert_record.issue_uts = issue_uts
        # The record could have picked up an error while retrying, we can clear that now
        # cert_record.error = None

        # cert_record.save()
        # CertificateEvent.record(CertificateEventType.COLLECTED, cert_record)

        # return True
        # end!

        if task.retries == 0 or HUEY.immediate:
            # If it did not pass, set the order to invalid. The consumer will have
            # to handle resubmission.
            logger.info(f"{log_prefix}: retries exceeded, marking order and invalid")
            order_service.update_status(order, OrderStatus.invalid)
        # ChallengeEvent.record(ChallengeEventType.RETRIES_EXCEEDED, challenge)
        # challenge.status = Status.objects.get(name="invalid")
        # challenge.save()

        # challenge.authorization.status = challenge.status
        # challenge.authorization.save()
        # else:
        #    task.retries -= 1
        #    raise RetryTask("Finalization unsuccessful")
