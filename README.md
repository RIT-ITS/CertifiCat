# Setup

This is intended to run in a [VSCode Dev Container](https://code.visualstudio.com/docs/devcontainers/containers). If you're not using dev containers, look at the Docker files in the .devcontainer folder for a functional dev environment.

## Add Database

Set up local databases for development and testing.

```bash
MYSQL_PWD=$CERTIFICAT__DB__PASSWORD mariadb -h mariadb. -uroot -e "CREATE DATABASE certificat;CREATE DATABASE test_certificat;"
```
## Run Migrations

```bash
scripts/manage migrate
```

Optionally trust self-signed certificate created at .devcontainer/traefik/certs system-wide to avoid browser errors using the following command.

```bash
.devcontainer/trust-traefik-cert
```

This relies on the `update-ca-certificates` command being installed on your machine.

# Testing

Manually using the provided Certbot Container:
```bash
trust-traefik-cert
certbot certonly --standalone --server https://certificat.localtest.me/directory -d acme.edu
```

Using pytest

```bash
./scripts/test
```

Adding coverage report and adjusting params forwarded to pytest

```bash
./scripts/test --cov=certificat
```

# Deployment

The project supports creating and deploying feature variants before a version is accepted as live. 

- Create a new feature branch, for example `dev`
- Update your version to the new version you're working on. For example go from `1.0.1` -> `1.0.2`.
- Make your changes, check in and commit, then run `./scripts/release` to push out a tagged dev version

- To release your changes, merge to master, ensure your version is correct (`1.0.2` in this example) and run `scripts/release` to update versions in dependent files. This will create and release a new tag.


