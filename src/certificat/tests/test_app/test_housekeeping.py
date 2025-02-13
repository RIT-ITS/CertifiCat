import pytest
from django.test import Client
from ..conftest import NewOrderRet
from certificat.modules.acme import models as db
from acmev2.models import OrderStatus
from certificat.modules.tasks.housekeeping import delete_invalid_orders
from django.utils import timezone
from datetime import timedelta


@pytest.mark.django_db
def test_delete_invalid_orders(acme_neworder, web_client: Client):
    new_order: NewOrderRet = acme_neworder()
    order_id: str = new_order.response.uri.split("/")[-1]
    order = db.Order.objects.get(name=order_id)
    order.status = OrderStatus.invalid

    # Newly invalid orders should stick around for some time
    order.save()
    delete_invalid_orders()
    assert db.Order.objects.filter(name=order_id).exists()

    # Invalid orders created in the past (10 days here) should be deleted
    order.created_at = timezone.now() - timedelta(days=10)
    order.save()
    delete_invalid_orders()
    assert not db.Order.objects.filter(name=order_id).exists()
