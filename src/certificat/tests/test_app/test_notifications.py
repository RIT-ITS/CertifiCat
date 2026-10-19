import acme
import pytest

from certificat.settings.dynamic import (
    ApplicationSettings,
    NotificationEventConfig,
    NotificationSettings,
)
from certificat.tests.conftest import NewOrderRet
from certificat.tests.helpers import do_challenge, finalize_order

from ..conftest import notifications


class TestNotifications:
    def setup_notifications(
        self,
    ):
        ApplicationSettings.get().notifications = NotificationSettings(
            on_finalization_success=NotificationEventConfig(services=["pytest://"]),
            on_finalization_error=NotificationEventConfig(services=["pytest://"]),
        )

    @pytest.mark.slow
    @pytest.mark.withoutresponses
    @pytest.mark.django_db
    def test_finalization_success(
        self, acme_client: acme.client.ClientV2, acme_neworder
    ):
        self.setup_notifications()

        new_order: NewOrderRet = acme_neworder()
        order = do_challenge(acme_client, new_order.response)
        finalized_order = finalize_order(acme_client, order)

        assert finalized_order.body.status.name == "valid"
        # A valid order should have a notification
        assert len(notifications) == 1
