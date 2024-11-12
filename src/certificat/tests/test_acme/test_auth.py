from acmev2.settings import ACMESettings
import pytest
import acme.client
from certificat.modules.acme import models as db
from ..conftest import NewAcctRet, gen_acme_client


@pytest.mark.django_db
def test_anonymous_account(acme_client: acme.client.ClientV2, acme_newacct):
    new_acct: NewAcctRet = acme_newacct()
    assert acme_client.net.account is not None

    acct_id = new_acct.response.uri.split("/")[-1]
    assert db.Account.objects.filter(name=acct_id).exists()


@pytest.mark.django_db
def test_force_eab(acme_newacct, acme_settings: ACMESettings):
    with pytest.raises(Exception, match=r".*externalAccountRequired.*"):
        acme_settings.eab_required = True
        acme_newacct()


@pytest.mark.django_db
def test_eab(acme_client: acme.client.ClientV2, acme_newacct):
    new_acct: NewAcctRet = acme_newacct(with_eab=True)

    acct_id = new_acct.response.uri.split("/")[-1]
    acct_obj = db.Account.objects.get(name=acct_id)

    assert acct_obj.binding is not None
    assert acct_obj.binding.hmac_id == new_acct.binding.hmac_id


@pytest.mark.django_db
def test_rebind_eab(acme_client: acme.client.ClientV2, acme_newacct):
    with pytest.raises(Exception, match=r".*rebind.*"):
        new_acct: NewAcctRet = acme_newacct(with_eab=True)
        acme_newacct(
            acme_client=gen_acme_client(), with_eab=True, binding=new_acct.binding
        )
