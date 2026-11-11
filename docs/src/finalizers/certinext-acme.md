# CERTInext ACME Finalizer

<!-- md:config `certificat.finalizer[certinext-acme]` -->

The `certinext-acme` finalizer forwards orders to CERTInext through its ACME API. CERTInext requires a different ACME integration for single-domain and multi-domain certificates. This finalizer holds credentials for both and chooses one per order.

## How it works

The finalizer behaves like the [ACME finalizer](acme.md), with these differences:

- **Binding selection.** Orders with one identifier use `single_domain_binding`. Orders with more than one identifier use `multi_domain_binding`.
- **Upstream accounts.** Each binding registers and stores its own upstream account, keyed by its `account_kid`. See [Upstream account](acme.md#upstream-account).
- **Challenges.** CERTInext validates domains in advance, so no challenge setup is required. The DNS-01 verification and challenge webhook options of the `acme` finalizer are not available.

## Prerequisites

Create two ACME integrations in CERTInext:

1. Open [ACME API integrations](https://us.certinext.io/acmeApi).
2. Create an API credential of type `ACME` with the **InCommon OV SSL Certificate** product. This is the single-domain integration.
3. Create an API credential of type `ACME` with the **InCommon OV SSL Certificate UCC** product. This is the multi-domain integration.
4. Record the directory URL, key ID, and HMAC key for each integration.

The domains you issue certificates for must already be validated for your organization in CERTInext.

## Configuration

``` yaml
certificat:
  finalizer:
    type: "certinext-acme"
    single_domain_binding:
      directory: "https://acme-us.certinext.io/v1/directory"
      account_kid: "<single-domain key ID>"
      account_hmac_key: "<single-domain HMAC key>"
      account_email: "pki-team@acme.edu"
    multi_domain_binding:
      directory: "https://acme-us.certinext.io/v1/directory"
      account_kid: "<multi-domain key ID>"
      account_hmac_key: "<multi-domain HMAC key>"
      account_email: "pki-team@acme.edu"
    finalization_timeout: 90
```

| Option | Required | Default | Description |
|---|---|---|---|
| `single_domain_binding` | Yes | | Credentials of the **InCommon OV SSL Certificate** integration. |
| `multi_domain_binding` | Yes | | Credentials of the **InCommon OV SSL Certificate UCC** integration. |
| `finalization_timeout` | No | `90` | Seconds to poll the upstream order before failing. |

Each binding takes `directory`, `account_email`, `account_kid`, and `account_hmac_key`. See the [configuration reference](../configuration/index.md#certificat.finalizer[certinext-acme]).

## Troubleshooting

The order page shows the error returned by CERTInext. These errors usually point to the integration's configuration in CERTInext, such as the product, domain validation status, or credentials. The task worker logs rarely add detail. If the error is unclear, contact CERTInext support with the order details.

See also [ACME finalizer troubleshooting](acme.md#troubleshooting).
