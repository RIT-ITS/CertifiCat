# Production Deployment

This page describes how to deploy CertifiCat with a container engine, SAML authentication, and an upstream ACME certificate authority.

## Architecture

CertifiCat has two runtime components, both provided by the same container image:

- **Web server.** Serves the web interface and the ACME API through nginx and gunicorn on port `80`.
- **Task worker.** Validates challenges, submits orders to the certificate authority, and runs periodic housekeeping.

Both components need these external services:

- **Database.** MySQL/MariaDB or PostgreSQL.
- **Redis.** Task queue and cache.

## Prerequisites

### Container engine

CertifiCat is distributed as the `ghcr.io/rit-its/certificat` image. The examples use the Docker CLI, but any compatible container engine works.

### Database

Create a database and a user that can modify its schema. CertifiCat runs migrations at startup. Configure the connection in [certificat.db](../configuration/index.md#certificat.db.section). Set `type` to `mysql` for MySQL/MariaDB or `postgresql` for PostgreSQL.

### Redis

Create a Redis instance protected by a password. Configure the connection in [certificat.redis](../configuration/index.md#certificat.redis.section).

### TLS-terminating reverse proxy

The container serves plain HTTP on port `80`. Place a reverse proxy or load balancer in front of it to terminate TLS. The proxy must:

- Forward the original `Host` header.
- Set `X-Forwarded-For` and `X-Forwarded-Proto`.

### Upstream certificate authority

CertifiCat forwards certificate requests to an upstream certificate authority through a [finalizer](../finalizers/index.md). Most deployments use the [ACME finalizer](../finalizers/acme.md). From your certificate authority, collect:

- The ACME directory URL.
- An external account binding key ID and HMAC key, if required.

### SAML identity provider

You need the identity provider's metadata and the name of the attribute that carries group membership. Generate a key pair for the CertifiCat service provider:

``` bash
openssl req -x509 -newkey rsa:3072 -nodes -days 3650 \
  -subj "/CN=acme.edu" \
  -keyout sp.key -out sp.crt
```

## Configuration

### Choose the base URL

The base URL, [certificat.url_root](../configuration/index.md#certificat.url_root), is the public HTTPS address of CertifiCat. This guide uses `https://acme.edu`. The ACME directory is served at `<url_root>/directory`.

!!! warning
    If the base URL changes, existing ACME accounts become unusable. This is due to [request URL integrity](https://datatracker.ietf.org/doc/html/rfc8555#section-6.4).

### Choose administrators

Administrators are granted on sign-in from the identity provider's data. Set one or both of these options:

- [administrators](../configuration/index.md#certificat.authentication[saml].administrators): usernames that receive administrator privileges.
- [administrators_groups](../configuration/index.md#certificat.authentication[saml].administrators_groups): groups whose members receive administrator privileges.

Users removed from these lists lose administrator privileges at their next sign-in.

### Create the configuration file

Generate a secret key:

``` bash
tr -dc 'a-zA-Z0-9!@#$%^&*(-_=+)' < /dev/urandom | head -c 50; echo
```

Create `config.yml`:

```yaml title="config.yml"
certificat:
  secret_key: "<generated secret key>"
  url_root: "https://acme.edu"

  db:
    type: "mysql"            # or "postgresql"
    name: "certificat"
    user: "certificat"
    password: "<database password>"
    host: "db.acme.edu"

  redis:
    host: "redis.acme.edu"
    password: "<redis password>"

  authentication:
    type: "saml"
    administrators_groups:
      - "certificat-admins"
    group_attribute: "memberOf"
    attribute_mapping:
      mail: [username, email]
      uid: [username]
      eduPersonPrincipalName: [username]
      givenName: [first_name]
      sn: [last_name]
    sp:
      entity_id: "https://acme.edu/saml2"
      name: "CertifiCat"
      key_file: "/etc/certificat/sp.key"
      cert_file: "/etc/certificat/sp.crt"
    idp:
      local:
        - "/etc/certificat/idp-metadata.xml"

  finalizer:
    type: "acme"
    directory: "https://ca.example.com/acme/directory"
    account_email: "pki-team@my-institution.edu"
    account_kid: "<EAB key ID>"
    account_hmac_key: "<EAB HMAC key>"
```

The [configuration reference](../configuration/index.md) documents every option.

## Start CertifiCat

Place the configuration and key files in a `config` folder:

``` text
config/
  config.yml         <-- CertifiCat configuration
  sp.key             <-- SAML service provider private key
  sp.crt             <-- SAML service provider certificate
  idp-metadata.xml   <-- SAML identity provider metadata
```

!!! note
    The container runs as the `certificat` user (UID `102`). That user must be able to read every mounted file. Private keys are often readable only by the user who created them. Use user namespace remapping, or for testing only, run `sudo chown 102 ./config/*`.

Start the container with `CERTIFICAT__CONFIG` set to the configuration file's path:

``` bash
docker run --detach \
    -v "$(pwd)/config:/etc/certificat:z" \
    -e CERTIFICAT__CONFIG=/etc/certificat/config.yml \
    -p 8080:80 \
    ghcr.io/rit-its/certificat:latest start
```

The `start` command runs database migrations, then starts both the web server and the task worker.

### Container commands

| Command | Description |
|---|---|
| `start` | Run migrations, then start the web server and task worker. |
| `start_server` | Run migrations, then start only the web server. |
| `start_huey` | Start only the task worker. |
| `migrate` | Run database migrations and exit. |
| `manage <args>` | Run a Django management command, for example `manage huey_healthcheck`. |
| `shell` | Open a shell in the container. |

To scale the web server and task worker independently, run one container with `start_server` and one or more with `start_huey`, all using the same configuration. `examples/postgres.yaml` shows this layout.

## Register with the identity provider

CertifiCat publishes its SAML service provider metadata at `https://acme.edu/saml2/metadata/`. Register this metadata with your identity provider and release the attributes named in `attribute_mapping` and `group_attribute`.

Sign-in fails until the identity provider trusts CertifiCat. To troubleshoot, set [certificat.authentication.debug](../configuration/index.md#certificat.authentication[saml].debug) to `true` and review the container logs.

## Verify the deployment

1. Sign in as an administrator and open `https://acme.edu/admin/`.
2. Under **Health**, confirm that the task worker has reported in. It reports once a minute.
3. Work through the **Setup Checklist**:
4. Create an account at `https://acme.edu/accounts/` and request a certificate with Certbot, as in the [evaluation walkthrough](local.md#3-create-an-acme-account).