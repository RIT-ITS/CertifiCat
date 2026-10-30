import dns.name
import pytest

from certificat.modules.acme.backends.dns_provider import (
    create_txt_records,
    delete_txt_records,
)
from certificat.settings.dynamic import ACMEFinalizerDNS01ProviderSettings

PROVIDER = ACMEFinalizerDNS01ProviderSettings(
    name="route53", options={"auth_access_key": "access-key"}
)
RECORDS = [
    ("_acme-challenge.www.sub.example.edu", "token-1"),
    ("_acme-challenge.www.sub.example.edu", "token-2"),
]
NAMESERVERS = ["8.8.8.8"]


@pytest.fixture
def client(mocker):
    mocker.patch(
        "certificat.modules.acme.backends.dns_provider.dns.resolver.zone_for_name",
        return_value=dns.name.from_text("sub.example.edu"),
    )
    return mocker.patch("certificat.modules.acme.backends.dns_provider.Client")


@pytest.fixture
def operations(client):
    return client.return_value.__enter__.return_value


def test_create_txt_records(operations):
    operations.create_record.return_value = True

    create_txt_records(PROVIDER, RECORDS, NAMESERVERS)

    assert [c.args for c in operations.create_record.call_args_list] == [
        ("TXT", name, value) for name, value in RECORDS
    ]


def test_zone_from_soa_lookup(client, operations):
    operations.create_record.return_value = True

    create_txt_records(PROVIDER, RECORDS[:1], NAMESERVERS)

    config = client.call_args.args[0]
    assert config.resolve("lexicon:domain") == "sub.example.edu"
    assert config.resolve("lexicon:delegated") == "sub.example.edu"
    assert config.resolve("lexicon:route53:auth_access_key") == "access-key"


def test_create_txt_records_failure(operations):
    operations.create_record.return_value = False

    with pytest.raises(RuntimeError):
        create_txt_records(PROVIDER, RECORDS, NAMESERVERS)


def test_delete_txt_records_continues_after_error(operations, caplog):
    operations.delete_record.side_effect = [Exception("Connection Error"), True]

    delete_txt_records(PROVIDER, RECORDS, NAMESERVERS)

    assert operations.delete_record.call_count == 2
    assert "Error deleting DNS-01 challenge record" in caplog.text
