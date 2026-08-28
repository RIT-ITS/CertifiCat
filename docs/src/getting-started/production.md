# Production Example

The CertifiCat service is composed of two distinct parts:

- An ACME and HTML frontend.
- An asynchronous task queue for background and periodic tasks.

CertifiCat also has dependencies on Redis and a database engine such as MySQL/MariaDB or Postgres.

## Prerequisites

### Container Engine

CertifiCat is distributed as a container image. All examples are given using the Docker CLI, but any compatible container engine can be used.

### Redis Server

Redis is used to queue background tasks and as a general-purpose key-value cache. You must generate a password for your Redis connection. Redis is configured through the [certificat.redis](../configuration/index.md#certificat.redis.section) section of the configuration document.

### Database and User

In this example we'll be using MySQL. Create a database and a user that has access to modify the schema. The database is configured through the [certificat.db](../configuration/index.md#certificat.db.section) section of the configuration document.

## Configuration

### Determine Base Url

This is the base domain for the application. For the purposes of this example we will use `https://acme.edu`.
!!! warning
    If your base URL changes your existing ACME accounts will become unusable. This is due to [request URL integrity](https://datatracker.ietf.org/doc/html/rfc8555#section-6.4).

### Configure Authentication

CertifiCat prefers and best supports SAML authentication. That will be covered more in-depth on the features documentation.

### Create Configuration File

```yaml title="config.yml"
certificat: 
  # Django SECRET_KEY. This should be set to a unique, unpredictable value.
  secret_key: "a-long-generated-secret-key"
  # The url root is used to generate absolute urls to the application.
  url_root: "https://acme.edu"

  # The database instance is supplied as an external dependency
  db: 
    type: "mysql"
    name: # Database to use after a connection is established
    user: # User for the database connection
    password: # Password for the database connection
    host: # Host for the database connection

  # The Redis instance is supplied as an external dependency
  redis: 
    host: # Host for the redis connection
    password: # Password for the Redis connection

  # This is how a user authenticates to the website
  authentication:
    type: "saml"
    # A list of user principals who will automatically be given administrator privileges on login.
    administrators: []
    # A dictionary mapping of src:[target] where attributes are mapped 
    # from SAML responses to Django properties. 
    # The name (or translated name) of the group attribute in the returned SAML assertion
    group_attribute: "memberof"
    attribute_mapping:
      mail: [username, email]
      uid: [username]
      eduPersonPrincipalName: [username]
      givenName: [first_name]
      sn: [last_name]
    sp: 
      # SAML service entity id. It should be unique and a URI.
      entity_id: "https://acme.edu/saml2"
      # The SP name
      name: "CertifiCat"
      # The location of the PEM-formatted private key file
      key_file: "/etc/certificat/sp.key"
      # The location of the PEM-formatted public key file
      cert_file: "/etc/certificat/sp.crt"
    idp: 
      # A list of local metadata files. 
      local: 
        - "/etc/certificat/idp-metadata.xml"

  # The finalizer is responsible for forwarding the client's CSR 
  # and returning a certificate. This ACME finalizer is general-purpose
  # and can be used with most upstreams in the absence of a separate API.
  finalizer:
    type: "acme"
    # The URL of your upstream provider's directory
    directory: https://certificates.io/acme
    account_email: "noreply@acme.edu"
    # This is necessary if your upstream requires external account binding
    account_hmac_key: "your-provided-hmac-key"
    # This is necessary if your upstream requires external account binding
    account_kid: "your-provided-account-kid"
    
```

## Starting CertifiCat

Create a `config` folder with the necessary configuration files. 

``` bash
config/
  | config.yml         <-- CertifiCat config
  | sp.key             <-- CertifiCat SAML private key
  | sp.crt             <-- CertifiCat SAML public key
  | idp-metadata.xml   <-- SAML IdP metadata
```

Start a CertifiCat container with the `CERTIFICAT__CONFIG` environment variable set and the `config` folder mounted.

!!! note
    Ensure the container's `certificat` user has access to all mounted files. By default private keys are only readable by the generating user. Short-term grant read permission to the `102` user id, long-term employ user namespacing.

``` bash
# To resolve the above note: sudo chown 102 ./config/*
# This is a hack, do not use this in production without understanding
# the implications.

docker run -v `pwd`/config:/etc/certificat:z \
    -e CERTIFICAT__CONFIG=/etc/certificat/config.yml \
    -p 80:80 \
    -it ghcr.io/rit-its/certificat:latest start
```

This will run all database migrations and start both the front-end and task runner. At this point you should have a complete CertifiCat environment ready to issue certificates.

## Next Steps

Authentication will not work until metadata is exchanged with your SAML IdP. To view CertifiCat metadata, open your browser to [http://localhost/saml2/metadata/](http://localhost/saml2/metadata/). Note that identifiers and callbacks reference the `https://acme.edu` base URL that were configured earlier.

[Consult the configuration section](../../configuration) for more examples and troubleshooting.