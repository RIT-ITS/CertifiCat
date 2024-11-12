from certificat.settings.dynamic import ApplicationSettings
from huey.contrib.djhuey import db_periodic_task
from huey import crontab
from certificat.modules.acme import models as db
from django.utils import timezone
from certificat.modules.acme.models import OrderStatus
import inject
from acmev2.services import IOrderService
import logging


logger = logging.getLogger(__name__)


@db_periodic_task(crontab(minute="*/10"))
def expire_orders_task(task=None):
    order_service = inject.instance(IOrderService)

    expired_orders = db.Order.objects.filter(
        status__in=[OrderStatus.pending, OrderStatus.processing, OrderStatus.ready],
        expires__lte=timezone.now(),
    )
    for order in expired_orders:
        logger.info("resolving state for expired order " + order.name)
        order_service.resolve_state(db.to_pydantic(order))


@db_periodic_task(crontab(day="*"))
def delete_invalid_orders(task=None):
    settings = inject.instance(ApplicationSettings)
    if not settings.delete_invalid_orders:
        logger.info("skipping delete task due to settings")
        return

    invalid_orders = db.Order.objects.filter(status=OrderStatus.invalid)
    logger.info(f"deleting {invalid_orders.count()} invalid orders")
    invalid_orders.delete()
