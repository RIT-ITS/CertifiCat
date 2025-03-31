# RIT CertifiCat
### Overview

Rochester Institute of Technology’s CertifiCat is an ACME (Automated Certificate Management Environment) server that allows streamlined and efficient certificate management. RIT CertifiCat runs in your data center to make it easier to issue certificates to hosts with private IP addresses, restrictive inbound firewalls, or no internet access.

### Features
 - **ACME**: Tested with common ACME clients
   - Certbot
   - getssl
   - acme.sh
   - Posh-ACME
   - CNCF cert-manager
 - **Certificate Authorities**:
   - Sectigo Certificate Manager (REST API)
   - Local certificate authority
 - **ACME Challenges**:
   - HTTP-01
 - **Authentication**:
   - SAML SSO with group access to ACME accounts
 - **Visualization**:
   - An attractive heat map
 - **Deployment methods**:
   - Docker
   - Kubernetes
   - Bare-metal
 - **Other features**:
   - RFC 1918 IP support
   - ACME toolkit to make EAB binding and key conversion easier
   - certificat-ps PowerShell module to make automating Posh-ACME easier

### Getting Help
Use the GitHub issues feature if you encounter a bug or have questions. We’ll do our best to provide answers.

### Supporting the Project
GitHub pull requests are welcomed. If you have an idea, submit it as an issue, and we’ll look it over. If you want to help with more than bug fixes or ideas, contact the project owners at its-acme@rit.edu.

# Development Quickstart

### Add Databases

Create two databases, one for development and one for running tests.

```bash
MYSQL_PWD=$CERTIFICAT__DB__PASSWORD mariadb -h mariadb. -uroot -e "CREATE DATABASE certificat;CREATE DATABASE test_certificat;"
```

### Run Migrations

```bash
scripts/manage migrate
```

Optionally, trust self-signed certificate created at .devcontainer/traefik/certs system-wide.

### Open Site Locally

Navigate to https://certificat.localtest.me and log in with one of the passwords in src/certificat_dev/saml/simple_saml_auth.php

# Testing

Run tests with the included run-tests script:

```bash
./scripts/run-tests
```

any additional parameters will be forwarded to `pytest`.

# Deployment

The project supports creating and deploying feature variants before a version is accepted as live. 

- Create a new feature branch, for example `dev`
- Update your version to the new version you're working on. For example go from `1.0.1` -> `1.0.2`.
- Make your changes, check in and commit, then run `./scripts/release` to push out a tagged dev version

- To release your changes, merge to master, ensure your version is correct (`1.0.2` in this example) and run `scripts/release` to update versions in dependent files. This will create and release a new tag.