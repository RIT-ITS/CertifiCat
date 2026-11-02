import logging

import dns.resolver
from lexicon.client import Client
from lexicon.config import ConfigResolver

from certificat.modules.acme.util import create_resolver
from certificat.settings.dynamic import ACMEFinalizerDNS01ProviderSettings

logger = logging.getLogger(__name__)


def _lexicon_config(
    settings: ACMEFinalizerDNS01ProviderSettings, name: str, nameservers: list[str]
) -> ConfigResolver:
    # Zone from the record's SOA via the verification nameservers, as lego does;
    # "delegated" stops lexicon guessing it from the public suffix list.
    zone = dns.resolver.zone_for_name(name, resolver=create_resolver(nameservers))
    zone = zone.to_text(omit_final_dot=True)
    return ConfigResolver().with_dict(
        {
            "provider_name": settings.name,
            "domain": zone,
            "delegated": zone,
            settings.name: settings.options,
        }
    )


def create_txt_records(
    settings: ACMEFinalizerDNS01ProviderSettings,
    records: list[tuple[str, str]],
    nameservers: list[str],
) -> None:
    for name, value in records:
        logger.info("Creating DNS-01 challenge record %s", name)
        with Client(_lexicon_config(settings, name, nameservers)) as operations:
            if not operations.create_record(rtype="TXT", name=name, content=value):
                raise RuntimeError(f"DNS provider failed to create TXT record {name}")


def delete_txt_records(
    settings: ACMEFinalizerDNS01ProviderSettings,
    records: list[tuple[str, str]],
    nameservers: list[str],
) -> None:
    for name, value in records:
        logger.info("Deleting DNS-01 challenge record %s", name)
        # The order outcome is already decided, so a leftover record is only logged.
        # Lexicon providers raise arbitrary types, hence the broad catch.
        try:
            with Client(_lexicon_config(settings, name, nameservers)) as operations:
                deleted = operations.delete_record(
                    rtype="TXT", name=name, content=value
                )
        except Exception:
            logger.exception("Error deleting DNS-01 challenge record %s", name)
            continue

        if not deleted:
            logger.error("DNS provider failed to delete TXT record %s", name)
