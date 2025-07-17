import logging

from certificat.modules.acme.backends import (
    FinalizeResponse,
    Finalizer,
    NotReadyException,
)
from huey.contrib.djhuey import HUEY
from huey import RetryTask
from certificat.modules.acme import models as db
from acmev2.models import OrderStatus
from certificat.settings.dynamic import ApplicationSettings
import inject
from django.utils.module_loading import import_string
from acmev2.services import IOrderService
from django.db import transaction

logger = logging.getLogger(__name__)


def _run_task(order_name: str):
    app_settings = inject.instance(ApplicationSettings)
    log_prefix = "order " + order_name

    with transaction.atomic():
        order = db.Order.objects.select_for_update().get(name=order_name)
        if order.status == OrderStatus.valid:
            return True

        if order.status != OrderStatus.processing:
            logger.info(f"{log_prefix}: order in invalid state: {order.status}")

    csr = db.CertificateRequest.objects.get(order=order).csr

    logger.info(f"{log_prefix}: creating finalizer")
    finalizer_klass = import_string(app_settings.finalizer_module)
    finalizer: Finalizer = finalizer_klass()

    try:
        finalize_response: FinalizeResponse = finalizer.finalize(order, csr)
        if finalize_response.ok():
            db.TaggedEvent.record(db.OrderEventType.FINALIZATION_PASSED, order)
            # TODO: Move to service?
            order.status = OrderStatus.valid
            order.save()
        else:
            db.OrderFinalizationError.objects.create(
                order=order,
                error=f"{finalize_response.error.code}: {finalize_response.error.description}",
            )

        return finalize_response.ok()
    except NotReadyException:
        # Don't log this as an error, the order is just in a processing state
        logger.info(f"{log_prefix}: order was not ready, will be retried if possible")
    except Exception as exc:
        logger.exception(f"{log_prefix}: exception finalizing order")
        db.OrderFinalizationError.objects.create(order=order, error=str(exc))

    return False


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
        except Exception:
            logger.exception("error in order finalization")

        if passed:
            return True

        if task.retries == 0 or HUEY.immediate:
            logger.info(f"{log_prefix}: retries exceeded, marking order as invalid")
            with transaction.atomic():
                order = db.Order.objects.select_for_update().get(name=order_name)
                if order.status == OrderStatus.valid:
                    return

                order_service = inject.instance(IOrderService)
                order_service.update_status(db.to_pydantic(order), OrderStatus.invalid)
                db.TaggedEvent.record(
                    db.OrderEventType.FINALIZATION_FAILED,
                    order,
                    payload={"reason": "Retries exceeded"},
                )
        else:
            task.retries -= 1
            raise RetryTask("Finalization unsuccessful")
