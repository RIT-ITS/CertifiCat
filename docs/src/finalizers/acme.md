# ACME Finalizer

<!-- md:config `certificat.finalizer[acme]` -->

The `acme` finalizer forwards each order to an upstream ACME server. It works with any certificate authority that offers an ACME API.

## How it works

For each order, the finalizer does the following:

1. Reads the upstream directory at `directory`.
2. Registers an upstream ACME account, or reuses the one it registered earlier. See [Upstream account](#upstream-account).
3. Creates an upstream order from the client's CSR.
4. Handles upstream challenges, unless `skip_answering_challenges` is `true`. See [Upstream challenges](#upstream-challenges).
5. Polls the upstream order until it is valid, for up to `finalization_timeout` seconds.
6. Stores the full certificate chain returned by the upstream server.

Any upstream error stops finalization and marks the order `invalid`, without retries. See [Retries and failures](index.md#retries-and-failures).

## Prerequisites

Collect the following from your certificate authority:

**Directory URL**
:   The upstream ACME JSON directory, usually ending in `/directory`.

**External account binding (EAB) credentials**
:   A key ID and an HMAC key, if your certificate authority requires external account binding. Most commercial certificate authorities do.

**Pre-authorized domains**
:   Many commercial certificate authorities validate domain ownership in advance, for example through organization or domain validation in their portal. In that case, the upstream server does not require challenges and you can set `skip_answering_challenges` to `true`.

## Configuration

``` yaml
certificat:
  finalizer:
    type: "acme"
    directory: "https://acme.ca.example/directory"
    account_email: "pki-team@acme.edu"
    account_kid: "<EAB key ID>"
    account_hmac_key: "<EAB HMAC key>"
    skip_answering_challenges: true
    finalization_timeout: 90
```

| Option | Required | Default | Description |
|---|---|---|---|
| <span style="white-space: nowrap;">`directory`</span> | Yes | | Upstream ACME directory URL. |
| <span style="white-space: nowrap;">`account_email`</span> | Yes | | Contact email for the upstream account. |
| <span style="white-space: nowrap;">`account_kid`</span> | No | | EAB key ID. |
| <span style="white-space: nowrap;">`account_hmac_key`</span> | No | | EAB HMAC key. |
| <span style="white-space: nowrap;">`skip_answering_challenges`</span> | No | `false` | Don't respond to upstream challenges. Use with upstream servers that pre-authorize domains. |
| <span style="white-space: nowrap;">`finalization_timeout`</span> | No | `90` | Seconds to poll the upstream order before failing. |

The [configuration reference](../configuration/index.md#certificat.finalizer[acme]) lists the same options.

## Upstream account

CertifiCat registers one upstream account the first time it finalizes an order:

- It generates a 2048-bit RSA account key, agrees to the upstream terms of service, and sends the EAB credentials if both `account_kid` and `account_hmac_key` are set.
- It stores the account key and URL in the database, keyed by `account_kid`.
- Later orders with the same `account_kid` reuse the stored account. All CertifiCat users share this one upstream account.

Stored accounts are listed under **ACME Finalizer Bindings** in the Django admin at `/admin/backend/`.

### Changing credentials

To use new EAB credentials, update `account_kid` and `account_hmac_key` and restart CertifiCat. A new upstream account is registered on the next order.

EAB credentials can be bound only once. If the upstream server reports that the credentials were already used, and the stored account was deleted or the database replaced, finalization fails with:

``` text
The ACME account has already been bound. Regenerate the ACME EAB credentials and restart the server with new account information.
```

Generate new EAB credentials with your certificate authority and update the configuration.

## Upstream challenges

CertifiCat can only satisfy `DNS-01` challenges. If you're using a server with pre-authorizations, you can skip challenge
configuration. Otherwise you will have to configure a method to satisfy upstream challenges

### Complete DNS-01 Configuration

``` yaml
certificat:
  finalizer:
    type: "acme"
    # ...
    challenges:
      dns_01:
        perform_verification: true
        verification_nameservers:
          - "1.1.1.1"
          - "8.8.8.8:53"
        verification_timeout: 60
    # Webhooks can be used to perform setup and teardown for DNS-01
    # challenges. Refer to the webhook documentation for payload info.
    webhooks:
      pre_answer_challenges:
        endpoint: "https://dns-automation.acme.edu/hooks/certificat"
        secret: "whsec_<base64-encoded secret>"
        timeout: 5
      post_answer_challenges:
        endpoint: "https://dns-automation.acme.edu/hooks/certificat"
        secret: "whsec_<base64-encoded secret>"
        timeout: 5
```

### DNS-01 verification

| Option | Default | Description |
|---|---|---|
| <!-- md:nowrap_key `challenges.dns_01.perform_verification` --> | <!-- md:nowrap_key `false` --> | Check that the `DNS-01` TXT records exist before answering. |
| <!-- md:nowrap_key `challenges.dns_01.verification_nameservers` --> | <!-- md:nowrap_key `["1.1.1.1"]` --> | Nameservers to query, as `ip` or `ip:port`. Every nameserver must return the expected TXT record. An empty list uses the system resolver which is almost never what you want. |
| <!-- md:nowrap_key `challenges.dns_01.verification_timeout` --> | `60` | Seconds to wait for all records. If the timeout is reached, the order becomes `invalid`. |

CertifiCat checks for a TXT record at `_acme-challenge.<domain>` containing the upstream challenge's validation value.

## Webhooks

The ACME finalizer supports webhooks to influence the flow externally. Webhooks are implemented using the [standard webhooks](https://www.standardwebhooks.com/) standard.

All webhooks use the following structure to define the external connection.

| Option | Required | Description |
|---|---|---|
| `endpoint` | Yes | URL that receives a `POST` request. |
| `secret` | Yes | Shared secret used to sign requests. `whsec_` followed by 24 to 64 Base64-encoded bytes. |
| `timeout` | No | Connect and read timeout for the request, in seconds. Defaults to `5`. |

Generate a secret with:

``` bash
echo "whsec_$(openssl rand -base64 32)"
```

### <!-- md:config `certificat.finalizer[acme].webhooks.pre_answer_challenges` `pre_answer_challenges` -->

This webhook is contacted after the finalizer has gathered the upstream challenges. Use this point to publish
DNS records or to interrupt an order from finalizing based on business logic.

### <!-- md:config `certificat.finalizer[acme].webhooks.post_answer_challenges` `post_answer_challenges` -->

This webhook is contacted after the finalizer has successfully answered challenges. Use this to clean up 
any DNS entries added in the `pre_answer_challenges` hook or to perform other business logic.

### Request signature

Requests are signed according to [Standard Webhooks](https://www.standardwebhooks.com/), using these headers:

| Header | Value |
|---|---|
| `webhook-id` | Unique message ID, prefixed with `msg_`. |
| `webhook-timestamp` | Send time in whole Unix seconds. |
| `webhook-signature` | `v1,` followed by the Base64-encoded HMAC-SHA256 signature. |

Verify requests with a [Standard Webhooks library](https://github.com/standard-webhooks/standard-webhooks#reference-implementations), using the same `secret`. For example, in Python:

``` python title="verify.py"
from standardwebhooks.webhooks import Webhook

def verify(secret: str, headers: dict, body: bytes) -> dict:
    # Raises WebhookVerificationError if the signature or timestamp is invalid
    return Webhook(secret).verify(body, headers)
```

Libraries reject requests with a timestamp more than five minutes from the current time.

## Troubleshooting

**`Error reading ACME directory at '<url>'`**
:   The task worker could not fetch `directory`. Check the URL and outbound network access from the task worker.

**`Upstream timed out while finalizing the order`**
:   The upstream order was not valid within `finalization_timeout` seconds. Increase the timeout, or check the order's status with your certificate authority.

**`urn:ietf:params:acme:error:...`**
:   The upstream server rejected the request. The description and detail come from the certificate authority.

**`Timeout reached verifying DNS challenges.`**
:   At least one nameserver in `verification_nameservers` did not return the expected TXT record within `verification_timeout` seconds.
