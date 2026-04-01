# Development Quickstart

The project is designed to be run using [VSCode devcontainers](https://code.visualstudio.com/docs/devcontainers/containers). Build and open the project in a dev container and open a terminal to use the following quickstart commands.

### Add Databases

Create two databases, one for development and one for running tests. 

#### MySQL Engine

```bash
MYSQL_PWD=$CERTIFICAT__DB__PASSWORD mariadb -h mariadb. -uroot -e "CREATE DATABASE certificat;CREATE DATABASE test_certificat;"
```

#### Postgres Engine
```bash
PGPASSWORD=$CERTIFICAT__DB__PASSWORD psql -U postgres -h postgres. -c "CREATE DATABASE certificat;" -c "CREATE DATABASE test_certificat;"
```

### Run Migrations

```bash
omnidev django migrate
```

### Start Services

```bash
omnidev start-services
```

### Open Site Locally

Its recommended to use a Docker-aware proxy like Traefik to manage routing. An example has been provided in the repo.

#### Traefik Example
```bash
docker-compose -f .devcontainer/traefik.yml up --detach
```

Go to https://certificat.dev.localhost and use the secret key generated in your `.devcontainer/.env` file.

# Testing

Run tests in the dev container with the included omnidev script:

```bash
omnidev test
```

any additional parameters will be forwarded to `pytest`.

Outside of the container, run the `scripts/run-tests` script to run the suite against MariaDB and Postgres.

# Releasing a New Version

Check in code and create a tag in the X.Y.Z(-dev1)? tag format. For example:

1. 1.0.5
2. 1.14.1
3. 2.0.0-dev1