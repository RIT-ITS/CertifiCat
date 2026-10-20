import acme.client
import pytest

from certificat.settings.dynamic import LocalACMESettings

from ..conftest import NewAcctRet


@pytest.mark.django_db
def test_mask_account_update(
    acme_client: acme.client.ClientV2,
    acme_newacct,
    acme_neworder,
    acme_settings: LocalACMESettings,
):
    acme_settings.mask_account_update = True
    new_acct: NewAcctRet = acme_newacct(with_eab=True)

    registration = acme_client.update_registration(
        new_acct.response,
        update=new_acct.response.body.update(contact=("mailto:updated@acme.edu",)),
    )

    assert registration.uri == new_acct.response.uri
    assert registration.body.status == "valid"
