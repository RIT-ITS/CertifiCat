# SAML Evaluation Stack

The SAML evaluation stack is the [local evaluation stack](local.md) with SAML sign-in instead of a local password. It includes a test identity provider (PyIDP) so you can see how users, attributes, and administrator privileges flow from an identity provider into CertifiCat.

!!! warning
    The SAML example uses known keys and secrets and an insecure local certificate authority. Use it only for local testing.

## What the stack contains

The stack is defined in `examples/saml.yaml` and its configuration is in `examples/saml/config.yaml`.

| Service | Purpose |
|---|---|
| `web` | The web interface and ACME server, started with `start_server`. Published on port `8000`. |
| `tasks` | The background task worker, started with `start_huey`. |
| `idp` | PyIDP, a test SAML identity provider. Published on port `8001`. |
| `mariadb` | Database. |
| `redis` | Task queue and cache. |

Metadata is already exchanged in this stack. CertifiCat reads the identity provider's metadata from `http://idp./saml2/metadata`, and the identity provider receives CertifiCat's metadata through its `SP_METADATA` environment variable. In a production deployment you exchange metadata yourself, as described in [Production Deployment](production.md#register-with-the-identity-provider).

## Prerequisites

The prerequisites are the same as for the [local evaluation stack](local.md#prerequisites). Port `8001` must also be free.

## Walkthrough

### 1. Start the stack

From the repository root:

``` bash
docker compose -f examples/saml.yaml up --detach
```

### 2. Sign in through the identity provider

1. Open [http://localhost:8000](http://localhost:8000). CertifiCat redirects you to PyIDP.
2. When PyIDP asks for a secret token, enter `password`.
3. Under the custom profile form, set **Username** to `admusr`. Fill in the remaining fields with any values.
4. Select **Log In With Profile**.

PyIDP sends a SAML assertion back to CertifiCat, which creates the user and signs you in.

`admusr` is listed in [administrators](../configuration/index.md#certificat.authentication[saml].administrators) in the example configuration, so this user is granted administrator privileges at sign-in. The predefined PyIDP profiles, such as `admin@acme.edu`, sign in as regular users.

### 3. Inspect the attribute mapping

The example configuration maps SAML attributes to CertifiCat user fields:

``` yaml
attribute_mapping:
  mail: [username, email]
  uid: [username]
  eduPersonPrincipalName: [username]
  givenName: [first_name]
  sn: [last_name]
```

PyIDP sends the **Username** field as `uid`. Because the example enables `debug`, the `web` container logs the raw attributes it receives at each sign-in:

``` bash
docker compose -f examples/saml.yaml logs web | grep "raw attributes"
```

Use these log lines to work out the mapping for your own identity provider. See [attribute_mapping](../configuration/index.md#certificat.authentication[saml].attribute_mapping).

### 4. Request a certificate

Follow the [local evaluation walkthrough](local.md#3-create-an-acme-account) from step 3 to create an account, register Certbot, and request a certificate. The steps are the same.

### 5. Stop the stack

``` bash
docker compose -f examples/saml.yaml down --volumes
```

## Next steps

[Deploy CertifiCat for production use.](production.md)
