MYSQL_DB_YAML_EXAMPLE = """``` yaml
certificat:
  db: 
    type: "mysql"
    host: "mariadb.my.edu"
    name: "certificat"
    user: "certificat_user"
    password: "super-s3cret-p@ssw0rd"
```"""

POSTGRES_DB_YAML_EXAMPLE = """``` yaml
certificat:
  db: 
    type: "postgresql"
    host: "postgres.my.edu"
    name: "certificat"
    user: "certificat_user"
    password: "super-s3cret-p@ssw0rd"
```"""

LOCAL_FINALIZER_EXAMPLE = """``` yaml
certificat:
  finalizer: 
    type: local
    key: |
      -----BEGIN RSA PRIVATE KEY-----
      MIIEowIBAAKCAQEAld0nGypEoP0EKuY1K7PA7auFw94EZy0l2KkbkOcgsdykDcka
      ...GENERATE-YOUR-OWN...
      Wo7xleX2mpTnHQTjtv1NikkMkcIVMz0Y2pbLbhkYyQVG2v6lL4jB
      -----END RSA PRIVATE KEY-----
    cert: |
      -----BEGIN CERTIFICATE-----
      MIIC1DCCAbygAwIBAgIUQbnQ870aDubvty1Ph5DcCq92JnowDQYJKoZIhvcNAQEL
      ...GENERATE-YOUR-OWN...
      0aRuPpTug5Kgc1VrD97fjbNVn5Q/v0d8eL+eB7jujTSSXg/iBTH9D/0MSTp0u2Mm
      qIQFqQ2WEBc=
      -----END CERTIFICATE-----  
```"""

ACME_FINALIZER_EXAMPLE = """``` yaml
certificat:
  finalizer: 
    type: "acme"
    directory: "https://acme.com/directory"
    account_kid: "atTXZtcIpapuQnvikq...jkH1EagEJJoi7Ae"
    account_hmac_key: "Uaf92GO53kY8DJRw...eoYvyJLUUDoLiF"
    account_email: "contact@acme.edu"
```"""

CERTINEXT_ACME_FINALIZER_EXAMPLE = """``` yaml
certificat:
  finalizer: 
    type: "certinext-acme"
      # This binding should use a single-domain non-UCC profile
      single_domain_binding:
        directory: "https://acme-us.certinext.io/v1/directory"
        account_kid: "atTXZtcIpapuQnvikq...jkH1EagEJJoi7Ae"
        account_hmac_key: "Uaf92GO53kY8DJRw...eoYvyJLUUDoLiF"
        account_email: "contact@acme.edu"
      # This binding should use a UCC profile
      multi_domain_binding:
        directory: "https://acme-us.certinext.io/v1/directory"
        account_kid: "1emo4ehgTQyT9R...MPY6IjOL5EHm4PSmNL"
        account_hmac_key: "vYELs8X22sXymmQh6...e59l6IeAaSL0G4"
        account_email: "contact@acme.edu"
```"""

SAML_AUTH_EXAMPLE = """``` yaml
certificat:
  authentication:
    type: saml
    administrators:
      - admin_username
    administrators_groups:
      - admin-group1
      - admin-group2
    attribute_mapping:
      mail: [username, email]
      uid: [username]
      eduPersonPrincipalName: [username]
      givenName: [first_name]
      sn: [last_name]
    sp:
      entity_id: "https://certificat.my.edu/saml2/metadata/"
      # key file mounted in the container
      key_file: "/etc/certificat/sp.key"
      # cert file mounted in the container
      cert_file: "/etc/certificat/sp.crt"
    idp:
      local: 
        # the location of the IdP metadata
        - "/etc/certificat/idp-metadata.xml"
```"""

REMOTE_AUTH_EXAMPLE = """``` yaml
certificat:
  authentication:
    type: remote
    administrators:
      - admin_username
    administrators_groups:
      - admin-group1
      - admin-group2
    user_header: HTTP_USER
    attribute_mapping:
      HTTP_MAIL: [email]
      HTTP_FIRSTNAME: [first_name]
      HTTP_LASTNAME: [last_name]
    redirect_template: https://auth.my.edu/authenticate?redirect={redirect}
```"""

CERTINEXT_FINALIZER_EXAMPLE = """
!!! warning
    This finalizer is not ready for production and should not be used even in a test state. Instead use a variant of the ACME finalizer
    to bind to CERTInext's ACME accounts. **Do not use this finalizer**.
"""

# TODO: Test that these examples load without throwing an exception
example_map = {
    "certificat.db.type.mysql": MYSQL_DB_YAML_EXAMPLE,
    "certificat.db.type.postgresql": POSTGRES_DB_YAML_EXAMPLE,
    "certificat.finalizer.type.local": LOCAL_FINALIZER_EXAMPLE,
    "certificat.finalizer.type.acme": ACME_FINALIZER_EXAMPLE,
    "certificat.finalizer.type.certinext-acme": CERTINEXT_ACME_FINALIZER_EXAMPLE,
    "certificat.finalizer.type.certinext": CERTINEXT_FINALIZER_EXAMPLE,
    "certificat.authentication.type.saml": SAML_AUTH_EXAMPLE,
    "certificat.authentication.type.remote": REMOTE_AUTH_EXAMPLE,
}
