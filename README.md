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

# Getting Started

Container quickstart coming soon.

# Full Config
```yaml
certificat: 
  # Debug mode for the application. This should never be True for production.
  debug: False
  # Django SECRET_KEY. This should be set to a unique, unpredictable value.
  secret_key: a-long-generated-secret-key
  time_zone: "America/New_York"
  # The url root is used to generate absolute urls to the application.
  url_root: https://acme.edu
  logging: 
    certificat_level: "INFO"
    huey_level: "INFO"
    django_level: "INFO"
    acmev2_level: "INFO"
  db: 
    engine: "django.db.backends.mysql"
    # The database to use after a connection is established.
    name: 
    # User for the database connection.
    user: 
    # Password for the database connection
    password: 
    # Host for the database connection
    host: 
    port: 3306
    # An optional table prefix for every table in the database.
    table_prefix: ""
  redis: 
    # Host for the redis connection.
    host: 
    # Password for the Redis connection
    password: 
    port: 6379
  task_queue: 
    # Number of workers in the Huey task queue.
    workers: 100
  # Signals to the app to trust the HTTP_X_FORWARDED_PROTO header if True.
  trust_proxy_forwarded_proto: False
  # Default login method for the app. This defaults to saml, the app has 
  # minimal support for local outside of debugging and examples.
  # Valid values: "local" 
  #               "saml"
  login_method: "saml"
  # The length of the hmac id generated for an ACME external account binding.
  hmac_id_length: 40
  # The length of the hmac key generated for an ACME external account binding.
  hmac_key_length: 90
  # How long to wait between challenge retries in seconds.
  challenge_retry_delay: 2
  # How many challenge retries to perform before marking the challenge invalid.
  challenge_max_retries: 5
  # How long to wait between order finalization retries in seconds.
  finalize_retry_delay: 10
  # How many order finalization retries to perform before marking the order invalid.
  finalize_max_retries: 10
  # Which order finalizer module to use. The server is designed to finalize 
  # all requests against one backend.
  # Valid values: "certificat.modules.acme.backends.sectigo.SectigoFinalizer"
  #               "certificat.modules.acme.backends.local.LocalFinalizer"
  finalizer_module: "certificat.modules.acme.backends.local.LocalFinalizer"
  # If set to True, invalid orders will be purged after some time.
  delete_invalid_orders: True

saml:
  # The debug setting for the Django SAML plugin.
  debug: False
  # The absolute path to the xmlsec binary.
  xmlsec_binary: "/usr/bin/xmlsec1"
  # The name of the session cookie.
  session_cookie: "snickerdoodle"
  # A list of user principals who will automatically be given administrator privileges on login.
  administrators: []
  # The name (or translated name) of the group attribute in the returned SAML assertion
  group_attribute: "memberof"
  # New groups synced from SAML will be prefixed with this identifier.
  group_sync_prefix: "SAML/"
  sp: 
    # SAML service entity id. It should be unique and a URI.
    entity_id: 
    # The SP name
    name: "CertifiCat"
    # The location of the PEM-formatted private key file
    key_file: /abs/path/to/mounted/key
    # The location of the PEM-formatted public key file
    cert_file: /abs/path/to/mounted/cert
    # The default signing algorithm.
    signing_algorthm: "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"
    # The default digest algorithm
    digest_algorithm: "http://www.w3.org/2001/04/xmlenc#sha256"
    # Disable SSO session reuse on login
    force_authn: False
    # Allow IdP-initiated SSO.
    allow_unsolicited: True
  idp: 
    # A list of local metadata files. Provide one or all of the following.
    local: 
      - "/abs/path/to/idp-metadata.xml"
    # A list of remote metadata providers.
    remote: 
        # Metadata available at a URL
      - url: http://identity.acme.edu/metadata
        # Signging cert 
        cert: "/abs/path/to/identity.acme.edu.crt"
  # A dictionary mapping of src:[target] where attributes are mapped 
  # from SAML responses to Django properties. 
  attribute_mapping:
    mail: [username, email]
    uid: [username]
    eduPersonPrincipalName: [username]
    givenName: [first_name]
    sn: [last_name]

# Required for certificat.modules.acme.backends.local.LocalFinalizer module
local_finalizer:
  # Private CA key
  key: |
    -----BEGIN RSA PRIVATE KEY-----
    MIIEowIBAAKCAQEAld0nGypEoP0EKuY1K7PA7auFw94EZy0l2KkbkOcgsdykDcka
    ...
    Wo7xleX2mpTnHQTjtv1NikkMkcIVMz0Y2pbLbhkYyQVG2v6lL4jB
    -----END RSA PRIVATE KEY-----
  # Public CA key
  cert: |
    -----BEGIN CERTIFICATE-----
    MIIC1DCCAbygAwIBAgIUQbnQ870aDubvty1Ph5DcCq92JnowDQYJKoZIhvcNAQEL
    ...
    qIQFqQ2WEBc=
    -----END CERTIFICATE-----  

# Required for certificat.modules.acme.backends.sectigo.SectigoFinalizer module
sectigo_finalizer:
  # Organization or department ID
  org_id: 12345
  # The certificate profile ID, found in the cert-manager UI
  cert_profile_id: 12345
  # This must be a validity period supported by the cert profile id
  cert_validity_period: 90
  customer_uri: InCommon
  api_base: https://cert-manager.com/api/
  # The created API user in cert-manager
  api_user: api@acme.edu
  api_password: "password-for-api-user"
  # If the api user isn't able to approve, you'll need to create a second user with 
  # approval access.
  approval_api_user: api-approver@acme.edu
  approval_api_password: "password-for-api-approver-user"
  # This email will be sent certificate lifecycle alerts
  external_requester_override: certs@acme.edu
  
```

# Development Quickstart

The project is designed to be run using [VSCode devcontainers](https://code.visualstudio.com/docs/devcontainers/containers). Build and open the project in a dev container and open a terminal to use the following quickstart commands.

### Add Databases

Create two databases, one for development and one for running tests. 

```bash
MYSQL_PWD=$CERTIFICAT__DB__PASSWORD mariadb -h mariadb. -uroot -e "CREATE DATABASE certificat;CREATE DATABASE test_certificat;"
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

Go to https://certificat.localtest.me and use the secret key generated in your `.devcontainer/.env` file.

# Testing

Run tests with the included run-tests script:

```bash
omnidev test
```

any additional parameters will be forwarded to `pytest`.

