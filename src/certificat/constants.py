from types import MappingProxyType
from cryptography.x509.oid import (
    ExtensionOID,
)

EXTENSION_NAMES = MappingProxyType(
    {
        ExtensionOID.AUTHORITY_INFORMATION_ACCESS: "Authority Information Access",
        ExtensionOID.AUTHORITY_KEY_IDENTIFIER: "Authority Key Identifier",
        ExtensionOID.BASIC_CONSTRAINTS: "Basic Constraints",
        ExtensionOID.CERTIFICATE_POLICIES: "Certificate Policies",
        ExtensionOID.CRL_DISTRIBUTION_POINTS: "CRL Distribution Points",
        ExtensionOID.CRL_NUMBER: "CRL Number",
        ExtensionOID.DELTA_CRL_INDICATOR: "Delta CRL Indicator",
        ExtensionOID.EXTENDED_KEY_USAGE: "Extended Key Usage",
        ExtensionOID.FRESHEST_CRL: "Freshest CRL",
        ExtensionOID.INHIBIT_ANY_POLICY: "Inhibit anyPolicy",
        ExtensionOID.ISSUER_ALTERNATIVE_NAME: "Issuer Alternative Name",
        ExtensionOID.ISSUING_DISTRIBUTION_POINT: "Issuing Distribution Point",
        ExtensionOID.KEY_USAGE: "Key Usage",
        ExtensionOID.MS_CERTIFICATE_TEMPLATE: "MS Certificate Template",
        ExtensionOID.NAME_CONSTRAINTS: "Name Constraints",
        ExtensionOID.OCSP_NO_CHECK: "OCSP No Check",  # RFC 2560 does not really define a spelling
        ExtensionOID.POLICY_CONSTRAINTS: "Policy Constraints",
        ExtensionOID.POLICY_MAPPINGS: "Policy Mappings",
        ExtensionOID.PRECERT_POISON: "Precert Poison",  # RFC 7633
        ExtensionOID.PRECERT_SIGNED_CERTIFICATE_TIMESTAMPS: "Precertificate Signed Certificate Timestamps",  # RFC 7633  # NOQA: E501
        ExtensionOID.SIGNED_CERTIFICATE_TIMESTAMPS: "Signed Certificate Timestamps",  # RFC 7633
        ExtensionOID.SUBJECT_ALTERNATIVE_NAME: "Subject Alternative Name",
        ExtensionOID.SUBJECT_DIRECTORY_ATTRIBUTES: "Subject Directory Attributes",
        ExtensionOID.SUBJECT_INFORMATION_ACCESS: "Subject Information Access",
        ExtensionOID.SUBJECT_KEY_IDENTIFIER: "Subject Key Identifier",
        ExtensionOID.TLS_FEATURE: "TLS Feature",  # RFC 7633
    }
)
