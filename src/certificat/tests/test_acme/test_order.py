import acme.client
import pytest
from ..conftest import NewOrderRet, NewAcctRet
from certificat.modules.acme import models as db
from acmev2.settings import ACMESettings
from acmev2.models import AccountStatus


@pytest.mark.django_db
def test_order(acme_client: acme.client.ClientV2, acme_neworder):
    initial_order_cnt = db.Order.objects.count()
    new_order: NewOrderRet = acme_neworder()
    assert new_order.response.body.status.name == "pending"
    assert db.Order.objects.count() == initial_order_cnt + 1


@pytest.mark.django_db
def test_order_multiple_sans(acme_client: acme.client.ClientV2, acme_neworder):
    initial_order_cnt = db.Order.objects.count()
    san_count = 10
    cn = "acme.localhost"
    sans = [f"acme{i}.localhost" for i in range(san_count)]
    new_order: NewOrderRet = acme_neworder(cn=cn, sans=sans)

    assert new_order.response.body.status.name == "pending"
    assert len(new_order.response.body.identifiers) == san_count + 1
    assert len(new_order.response.body.authorizations) == san_count + 1
    assert db.Order.objects.count() == initial_order_cnt + 1

    identifiers = set(i.value for i in new_order.response.body.identifiers) | set([cn])
    assert set(sans) | set([cn]) == identifiers


@pytest.mark.django_db
def test_blacklisted_domain(acme_neworder, acme_newacct, acme_settings: ACMESettings):
    acme_settings.blacklisted_domains = [r".*\.acme\.edu", r"acme\.edu"]
    new_acct: NewAcctRet = acme_newacct()

    acct_id = new_acct.response.uri.split("/")[-1]
    new_acct = NewAcctRet(
        **(new_acct._asdict() | {"user": db.Account.objects.get(name=acct_id)})
    )

    with pytest.raises(
        Exception, match=r".*urn:ietf:params:acme:error:rejectedIdentifier.*"
    ):
        acme_neworder(cn="acme.edu", sans=["acme.edu"], new_acct=new_acct)

    with pytest.raises(
        Exception, match=r".*urn:ietf:params:acme:error:rejectedIdentifier.*"
    ):
        acme_neworder(cn="sub.acme.edu", sans=["sub.acme.edu"], new_acct=new_acct)

    # Just needs to pass without raising an exception, no assertion necessary
    acme_neworder(cn="acme2.edu", sans=["acme2.edu"], new_acct=new_acct)


@pytest.mark.django_db
def test_order_from_invalid_account(
    acme_client: acme.client.ClientV2, acme_neworder, acme_newacct
):
    new_acct: NewAcctRet = acme_newacct()

    acct_id = new_acct.response.uri.split("/")[-1]
    new_acct = NewAcctRet(
        **(new_acct._asdict() | {"user": db.Account.objects.get(name=acct_id)})
    )

    # Ensure revoked user can't create order
    new_acct.user.status = AccountStatus.revoked
    new_acct.user.save()

    with pytest.raises(Exception, match=r".*Account not valid.*"):
        acme_neworder(new_acct=new_acct)

    # Ensure deacivated user can't create order
    new_acct.user.status = AccountStatus.deactivated
    new_acct.user.save()

    with pytest.raises(Exception, match=r".*Account not valid.*"):
        acme_neworder(new_acct=new_acct)

    # Ensure the same user as valid can create an order!
    new_acct.user.status = AccountStatus.valid
    new_acct.user.save()

    acme_neworder(new_acct=new_acct)
