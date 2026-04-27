MYSQL_DB_YAML_EXAMPLE = """yaml
certificat:
  db: 
    type: "mysql"
    host: "mariadb.my.edu"
    name: "certificat"
    user: "certificat_user"
    password: "super-s3cret-p@ssw0rd"
"""

POSTGRES_DB_YAML_EXAMPLE = """yaml
certificat:
  db: 
    type: "postgresql"
    host: "postgres.my.edu"
    name: "certificat"
    user: "certificat_user"
    password: "super-s3cret-p@ssw0rd"
"""

LOCAL_FINALIZER_EXAMPLE = """yaml
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
"""

SAML_AUTH_EXAMPLE = """yaml
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
      remote: 
        # the location of the IdP metadata
        - url: "http://idp.my.edu/saml2/metadata"
"""

REMOTE_AUTH_EXAMPLE = """yaml
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
"""

example_map = {
    "certificat.db.type.mysql": MYSQL_DB_YAML_EXAMPLE,
    "certificat.db.type.postgresql": POSTGRES_DB_YAML_EXAMPLE,
    "certificat.finalizer.type.local": LOCAL_FINALIZER_EXAMPLE,
    "certificat.authentication.type.saml": SAML_AUTH_EXAMPLE,
    "certificat.authentication.type.remote": REMOTE_AUTH_EXAMPLE,
}
