# Alternative Finalizers

<!-- md:config `certificat.alternative_finalizers` -->

By default, every account uses the finalizer in `certificat.finalizer`. Alternative finalizers let you send a specific account's orders to a different certificate authority or product. For example, a few accounts could use a separate ACME integration with a different certificate profile.

## Configuration

Add each alternative finalizer to `certificat.alternative_finalizers`. The `finalizer` key takes the same options as [certificat.finalizer](../configuration/index.md#certificat.finalizer.section).

``` yaml
certificat:
  finalizer:
    type: "acme"
    directory: "https://acme.ca.example/directory"
    account_email: "pki-team@acme.edu"
    account_kid: "<default key ID>"
    account_hmac_key: "<default HMAC key>"

  alternative_finalizers:
    - id: "ev-certificates"
      name: "EV certificates"
      description: "Extended validation profile. For public-facing payment sites."
      finalizer:
        type: "acme"
        directory: "https://acme.ca.example/ev/directory"
        account_email: "pki-team@acme.edu"
        account_kid: "<EV key ID>"
        account_hmac_key: "<EV HMAC key>"
```

| Option | Required | Description |
|---|---|---|
| `id` | Yes | Unique identifier, stored on each account that uses this finalizer. Don't change it after accounts are assigned. |
| `name` | Yes | Short name shown in the web interface. |
| `description` | Yes | Description shown in the web interface. |
| `finalizer` | Yes | Finalizer configuration, with the same options as `certificat.finalizer`. |

## Assign a finalizer to an account

Anyone who can edit an account can change its finalizer.

1. Open the account from **Accounts**.
2. On the **General Details** tab, find **Finalizer**.
3. Select the finalizer to use. Select **Default** to return the account to `certificat.finalizer`.

The finalizer is chosen each time an order is finalized, including retries. Orders finalized after the change use the selected finalizer.

The **Finalizer** field appears for users who can edit the account when at least one alternative finalizer is configured. Users who can only view the account see it, read-only, when the account uses a non-default finalizer.

## Removing an alternative finalizer

If you remove an alternative finalizer or change its `id`, accounts assigned to it use the default finalizer for new orders. Their account pages still show the old assignment until someone who can edit the account changes it.
