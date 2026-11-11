# Local Evaluation Stack

The evaluation stack runs a complete CertifiCat instance on your workstation with Docker Compose. Use it to request a test certificate with Certbot and explore the web interface before planning a production deployment.

!!! warning
    The evaluation stack uses known credentials, a local sign-in, and an insecure local certificate authority. Use it only for local testing. Do not trust or deploy certificates it issues.

## What the stack contains

The stack is defined in `examples/simple.yaml` and its configuration is in `examples/simple/config.yaml`.

| Service | Purpose |
|---|---|
| `certificat` | The web interface, ACME server, and background task worker in a single container.<br/>Started with the `start` command. Published on port `8000`. |
| `mariadb` | Database. Data is kept in the `mariadb-data` volume. |
| `redis` | Task queue and cache. |

The configuration differs from production in two ways:

- **Local sign-in.** A single administrator account (`admin` / `admin`) is created at startup. Local sign-in is intended only for evaluation and is not listed in the configuration reference.
- **Local finalizer.** Certificates are signed by a bundled test CA instead of an upstream certificate authority. See [Local Finalizer](../finalizers/local.md).

## Prerequisites

- Docker with the Compose plugin
- Git
- [Certbot](https://certbot.eff.org/)
- Port `80` free on your workstation. Certbot listens on it to answer the HTTP-01 challenge.

## Walkthrough

### 1. Start CertifiCat

Clone the repository and start the stack:

``` bash
git clone https://github.com/RIT-ITS/CertifiCat.git
cd CertifiCat
docker compose -f examples/simple.yaml up --detach
```

On first start the container runs database migrations and creates the administrator account. This can take a minute. Follow progress with:

``` bash
docker compose -f examples/simple.yaml logs --follow certificat
```

### 2. Sign in

Open [http://localhost:8000](http://localhost:8000) and sign in:

```text title="login credentials"
Username: admin
Password: admin
```

Optionally, open [http://localhost:8000/admin/](http://localhost:8000/admin/). The **Setup Checklist** lists what a production deployment still needs, and **Health** confirms that the task worker is running. The task worker reports once a minute, so a warning immediately after startup is expected.

### 3. Create an ACME account

1. Go to [http://localhost:8000/accounts/](http://localhost:8000/accounts/) and select **Create New Account**.
2. Leave **Access** set to **Personal**.
3. Enter a name and a note, accept the terms of service, and create the account.

The account page shows an **External Account ID**, an **External Account Key**, and a ready-to-run Certbot command.

### 4. Register Certbot

Copy the Certbot command from the account page. It has the following form:

``` bash
sudo certbot register \
    --server="http://localhost:8000/directory" \
    --eab-kid="<External Account ID>" \
    --eab-hmac-key="<External Account Key>" \
    --email="noreply@localhost"
```

Answer Certbot's prompts. When registration succeeds, refresh the account page. The account is now active and shows its orders and settings.

### 5. Request a certificate

``` bash
sudo certbot certonly \
  --standalone \
  --server http://localhost:8000/directory \
  --domain host.docker.internal
```

Certbot starts a temporary web server on port `80`. CertifiCat connects to `host.docker.internal`, which the stack maps to your workstation, to validate the HTTP-01 challenge. The task worker then signs the certificate with the local CA and Certbot saves it under `/etc/letsencrypt/live/host.docker.internal/`.

### 6. Review the results

- **Orders** at [http://localhost:8000/orders/](http://localhost:8000/orders/) lists each order with its status. Open an order to see its identifiers, authorizations, and event history.
- **Certificates** at [http://localhost:8000/certificates/](http://localhost:8000/certificates/) lists issued certificates. Open one to view its details and chain.

### 7. Stop the stack

``` bash
docker compose -f examples/simple.yaml down
```

Add `--volumes` to also remove the database. Accounts and certificates are deleted with it.

## Troubleshooting

**Certbot can't bind to port 80**
:   Stop the service that is using port `80` and run Certbot again.

**The order fails with a connection error during validation**
:   CertifiCat could not reach Certbot on port `80` of your workstation. Check that a host firewall allows connections from the Docker bridge network to port `80`.

**Certbot reports that the account does not exist**
:   The database was removed with `--volumes` but Certbot still has the old account. Delete the account directory for `localhost:8000` under `/etc/letsencrypt/accounts/`, then create a new CertifiCat account and register again.

**The order stays in `processing`**
:   The task worker isn't running or the finalizer failed. Check the container logs and the **Health** section of [http://localhost:8000/admin/](http://localhost:8000/admin/).

## Next steps

[Deploy CertifiCat for production use.](production.md)
