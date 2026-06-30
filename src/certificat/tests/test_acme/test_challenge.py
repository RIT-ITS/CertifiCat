from typing import List

import pytest
import acme.client
from ..helpers import do_challenge, select_failed_authorizations
from ..conftest import NewOrderRet
from certificat.modules.acme import models as db
import acme.messages


@pytest.mark.django_db
def test_successful_challenge(acme_client: acme.client.ClientV2, acme_neworder):
    new_order: NewOrderRet = acme_neworder()

    order = do_challenge(acme_client, new_order.response)

    failed_auth = select_failed_authorizations(order)
    assert not any(failed_auth), f"Failed auth for domain {failed_auth}"


@pytest.mark.django_db
def test_preauthorized_challenges(
    acme_client: acme.client.ClientV2, acme_neworder, acme_newacct
):

    acme_acct = acme_newacct()

    def run_test(
        all_domains: List[str], preauth_domains: List[str], expect_failure=False
    ):
        account = db.Account.objects.get(name=acme_acct.response.uri.split("/")[-1])
        for domain in preauth_domains:
            db.PreAuthorizedAccountIdentifier.objects.create(
                account=account,
                identifier_type=db.IdentifierType.dns,
                identifier_value=domain,
            )

        combined_domains = list(set(all_domains + preauth_domains))
        new_order: NewOrderRet = acme_neworder(
            new_acct=acme_acct, cn=combined_domains[0], sans=combined_domains
        )
        order = do_challenge(acme_client, new_order.response)

        failed_auth = select_failed_authorizations(order)
        if expect_failure:
            assert len(failed_auth) != 0
        else:
            assert len(failed_auth) == 0

    run_test([], ["preauth.acme.edu"])
    run_test(["acme.localhost"], ["preauth2.acme.edu"])
    run_test(["failing.localhost"], ["preauth3.acme.edu"], expect_failure=True)


@pytest.mark.django_db
def test_failed_challenge(acme_client: acme.client.ClientV2, acme_neworder):
    new_order: NewOrderRet = acme_neworder(cn="err.edu", sans=["err.edu"])

    order = do_challenge(acme_client, new_order.response)

    failed_auth = select_failed_authorizations(order)
    assert "err.edu" in failed_auth
    assert db.ChallengeError.objects.count() > 0


@pytest.mark.django_db
def test_nonexistent_challenge(acme_client: acme.client.ClientV2, acme_neworder):
    new_order: NewOrderRet = acme_neworder(cn="err.edu", sans=["err.edu"])
    # challenges was deleted for whatever reason
    db.Challenge.objects.all().delete()
    with pytest.raises(Exception, match=r".*resourceNotFound.*"):
        do_challenge(acme_client, new_order.response)
