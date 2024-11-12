import pytest
import acme.client
from ..helpers import do_challenge, select_failed_authorizations
from ..conftest import NewOrderRet
from certificat.modules.acme import models as db


@pytest.mark.django_db
def test_successful_challenge(acme_client: acme.client.ClientV2, acme_neworder):
    new_order: NewOrderRet = acme_neworder()

    order = do_challenge(acme_client, new_order.response)

    failed_auth = select_failed_authorizations(order)
    assert not any(failed_auth), f"Failed auth for domain {failed_auth}"


@pytest.mark.django_db
def test_failed_challenge(acme_client: acme.client.ClientV2, acme_neworder):
    new_order: NewOrderRet = acme_neworder(cn="err.edu", sans=["err.edu"])

    order = do_challenge(acme_client, new_order.response)

    failed_auth = select_failed_authorizations(order)
    assert "err.edu" in failed_auth
    assert db.ChallengeError.objects.count() > 0
