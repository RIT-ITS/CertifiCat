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
- Make your changes, if you need to deploy to Kubernetes run the `scripts/propagate-version` command before checking in. This will ensure the CI/CD pipeline runs and creates the correct artifacts.
- Save the version output from propagate-version. If your branch is `dev` an example version would be `1.0.0-dev.1735857817`
- Push your changes and create a tag. Your tag is the version that was just generated and will build the required packages for you to deploy this feature. The tag for this example would again be `1.0.0-dev.1735857817`. 

- To release your changes, merge to master, update your version (`1.0.1` in this example) and run `scripts/propagate-version` to update versions in dependent files. Again create a new tag `1.0.1` and this will create a new image and helm deployment.

# Tasks

[ ] - Move acmev2 to pypi
[ ] - add failed order retention time