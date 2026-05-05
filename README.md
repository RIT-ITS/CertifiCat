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
   - [certificat-ps PowerShell module](https://github.com/RIT-ITS/CertifiCat-PS) to make automating Posh-ACME easier

### Getting Help
Use the GitHub issues feature if you encounter a bug or have questions. We’ll do our best to provide answers.

### Supporting the Project
GitHub pull requests are welcomed. If you have an idea, submit it as an issue, and we’ll look it over. If you want to help with more than bug fixes or ideas, contact the project owners at its-acme@rit.edu.

# Getting Started

The CertifiCat service is composed of two distinct parts:

- An ACME and HTML frontend.
- An asynchronous task queue for background and periodic tasks.

CertifiCat also has dependencies on Redis and MariaDB. Refer to the examples directory for full compose files detailing how to set up a local environment.

# Quickstart Config
```yaml
certificat: 
  # Django SECRET_KEY. This should be set to a unique, unpredictable value.
  secret_key: "a-long-generated-secret-key"
  # The url root is used to generate absolute urls to the application.
  url_root: "https://acme.edu"
  logging: 
    certificat_level: "INFO"
    huey_level: "INFO"
    django_level: "INFO"
    acmev2_level: "INFO"
  db: 
    type: "mysql"
    # The database to use after a connection is established.
    name: 
    # User for the database connection.
    user: 
    # Password for the database connection
    password: 
    # Host for the database connection
    host: 
  redis: 
    # Host for the redis connection.
    host: 
    # Password for the Redis connection
    password: 
  authentication:
    type: "saml"
    # A list of user principals who will automatically be given administrator privileges on login.
    administrators: []
    # New groups synced from SAML will be prefixed with this identifier.
    group_sync_prefix: "SAML/"
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
      entity_id: 
      # The SP name
      name: "CertifiCat"
      # The location of the PEM-formatted private key file
      key_file: "/abs/path/to/mounted/key"
      # The location of the PEM-formatted public key file
      cert_file: "/abs/path/to/mounted/cert"
    idp: 
      # A list of local metadata files. Provide one or all of the following.
      local: 
        - "/abs/path/to/idp-metadata.xml"
      # A list of remote metadata providers.
      remote: 
          # Metadata available at a URL
        - url: "http://identity.acme.edu/metadata"
          # Signging cert 
          cert: "/abs/path/to/identity.acme.edu.crt"
  finalizer:
    type: "local"
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
```