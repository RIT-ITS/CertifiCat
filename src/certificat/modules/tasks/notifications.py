import logging

from huey.contrib.djhuey import db_task

from certificat import notifications
from certificat.modules.acme import models as db

logger = logging.getLogger(__name__)


@db_task()
def publish_finalization_success_task(order_name: str):
    order = db.Order.objects.get(name=order_name)
    notifications.publish_finalization_success(order)


@db_task()
def publish_finalization_error_task(order_name: str):
    order = db.Order.objects.get(name=order_name)
    notifications.publish_finalization_error(order)
