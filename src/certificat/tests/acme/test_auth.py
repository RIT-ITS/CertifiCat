import pytest
import acme.client
from certificat.modules.acme import models as db


@pytest.mark.django_db
def test_anonymous_account(acme_client: acme.client.ClientV2):
    registration = acme.client.messages.NewRegistration.from_data(
        email="testemail@rit.edu", terms_of_service_agreed=True
    )

    acct = acme_client.new_account(registration)

    assert acme_client.net.account is not None

    acct_id = acct.uri.split("/")[-1]
    assert db.Account.objects.filter(name=acct_id).exists()
