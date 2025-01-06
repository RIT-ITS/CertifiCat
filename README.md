# Setup

MYSQL_PWD=$CERTIFICAT__DB__PASSWORD mariadb -h mariadb. -uroot -e "CREATE DATABASE certificat;CREATE DATABASE test_certificat;"

Optionally trust self-signed certificate created at .devcontainer/traefik/certs system-wide.

# Testing

Certbot:

sudo certbot certonly --standalone --server http://localhost:8000/directory -d testcert.localhost

Caddyfile:

acmetest.localhost {
  tls {
    ca http://localhost:8000/directory
    eab hmac_id hmac_key
  }
}

# Deployment

The project supports creating and deploying feature variants before a version is accepted as live. 

- Create a new feature branch, for example `dev`
- Update your version to the new version you're working on. For example go from `1.0.1` -> `1.0.2`.
- Make your changes, check in and commit, then run `./scripts/release` to push out a tagged dev version

- To release your changes, merge to master, ensure your version is correct (`1.0.2` in this example) and run `scripts/release` to update versions in dependent files. This will create and release a new tag.

# Tasks

- Move acmev2 to pypi