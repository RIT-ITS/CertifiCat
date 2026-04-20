# Settings Documentation

| Key | Required | Default | Description |
| --- | --- | --- | --- |
| [`acme.authorization_client_delay`](#acme-authorization_client_delay) |  | `15` | - |
| [`acme.blacklisted_domains`](#acme-blacklisted_domains) |  | `[]` | - |
| [`acme.challenges_available`](#acme-challenges_available) |  | `["http-01"]` | - |
| [`acme.eab_required`](#acme-eab_required) |  | `false` | - |
| [`acme.http_01_challenge_user_agent`](#acme-http_01_challenge_user_agent) |  | `python-acmev2/0.1.2` | - |
| [`acme.mask_order_processing_status_ua_match`](#acme-mask_order_processing_status_ua_match) |  | `^cert-manager-clusterissuers.*` | - |
| [`acme.max_identifiers`](#acme-max_identifiers) |  | `50` | - |
| [`acme.resource_expiration_delta`](#acme-resource_expiration_delta) |  | `PT8H` | - |
| [`certificat.authentication`](#certificat-authentication) | ✓ | `-` | Authentication settings for the web frontend. |
| [`certificat.beacon_enabled`](#certificat-beacon_enabled) |  | `true` | If true, will send tracking information about usage to RIT. All tracking info is logged. |
| [`certificat.challenge_max_retries`](#certificat-challenge_max_retries) |  | `5` | How many challenge retries to perform before marking the challenge invalid. |
| [`certificat.challenge_retry_delay`](#certificat-challenge_retry_delay) |  | `2` | How long to wait between challenge retries in seconds. |
| [`certificat.db`](#certificat-db) | ✓ | `-` | Database engine settings. |
| [`certificat.delete_invalid_orders`](#certificat-delete_invalid_orders) |  | `true` | If set to True, invalid orders will be purged after some time. |
| [`certificat.finalize_max_retries`](#certificat-finalize_max_retries) |  | `10` | How many order finalization retries to perform before marking the order invalid. |
| [`certificat.finalize_retry_delay`](#certificat-finalize_retry_delay) |  | `10` | How long to wait between order finalization retries in seconds. |
| [`certificat.finalizer`](#certificat-finalizer) | ✓ | `-` | Which order finalizer module to use. The server is designed to finalize all requests against one backend. |
| [`certificat.healthcheck_allowed_networks`](#certificat-healthcheck_allowed_networks) |  | `["127.0.0.1/32"]` | Networks allowed to access the health endpoints. |
| [`certificat.hmac_id_length`](#certificat-hmac_id_length) |  | `40` | The length of the hmac id generated for an ACME external account binding. |
| [`certificat.hmac_key_length`](#certificat-hmac_key_length) |  | `90` | The length of the hmac key generated for an ACME external account binding. |
| [`certificat.logging.acmev2_level`](#certificat-logging-acmev2_level) |  | `INFO` | Logging level for ACME server component. |
| [`certificat.logging.certificat_level`](#certificat-logging-certificat_level) |  | `INFO` | Logging level for the CertifiCat frontend. |
| [`certificat.logging.django_level`](#certificat-logging-django_level) |  | `INFO` | Logging level for Django components. |
| [`certificat.logging.huey_level`](#certificat-logging-huey_level) |  | `INFO` | Logging level for the task runner. |
| [`certificat.redis.host`](#certificat-redis-host) | ✓ | `-` | Host for the redis connection. |
| [`certificat.redis.password`](#certificat-redis-password) | ✓ | `-` | Password for the Redis connection |
| [`certificat.redis.port`](#certificat-redis-port) |  | `6379` | Port for the Redis connection |
| [`certificat.secret_key`](#certificat-secret_key) | ✓ | `-` | Django SECRET_KEY. This should be set to a unique, unpredictable value. |
| [`certificat.show_version`](#certificat-show_version) |  | `false` | Show the version on the website. |
| [`certificat.task_queue.workers`](#certificat-task_queue-workers) |  | `100` | Number of workers in the Huey task queue. |
| [`certificat.theming.global_css`](#certificat-theming-global_css) |  | `null` | Global CSS injected into a style tag rendered on every page. |
| [`certificat.time_zone`](#certificat-time_zone) |  | `America/New_York` | Django time zone, used mostly for date localization. |
| [`certificat.trust_proxy_forwarded_proto`](#certificat-trust_proxy_forwarded_proto) |  | `false` | Signals to the app to trust the HTTP_X_FORWARDED_PROTO header if True. |
| [`certificat.url_root`](#certificat-url_root) | ✓ | `-` | The url root is used to generate absolute urls to the application. |

<a id="certificat-authentication" name="certificat-authentication"></a>

## `certificat.authentication`
This is a polymorphic property controlled by the `type` attribute. Use the following templates as an example of how to configure different `authentication` types.
- Required: `Yes`
- Description: Authentication settings for the web frontend.
- Types: [`remote`](#certificat-authentication-type-remote), [`saml`](#certificat-authentication-type-saml)

<a id="certificat-authentication-type-remote"></a>

### `certificat.authentication.type: remote`

| Key | Required | Default | Description |
| --- | --- | --- | --- |
| [`certificat.authentication.type`](#certificat-authentication-type) |  | `remote` | - |
| [`certificat.authentication.administrators`](#certificat-authentication-administrators) |  | `[]` | A list of user principals who will automatically be given administrator privileges on login. |
| [`certificat.authentication.force_logout_if_no_header`](#certificat-authentication-force_logout_if_no_header) |  | `true` | - |
| [`certificat.authentication.log_http_headers`](#certificat-authentication-log_http_headers) |  | `false` | - |
| [`certificat.authentication.redirect_template`](#certificat-authentication-redirect_template) | ✓ | `-` | Templated URL target for redirects. The redirect variable is substituted with the URL encoded path of the protected resource. |
| [`certificat.authentication.user_header`](#certificat-authentication-user_header) |  | `HTTP_USER` | - |

<a id="certificat-authentication-type-saml"></a>

### `certificat.authentication.type: saml`
```yaml
certificat:
  authentication:
    type: saml
    administrators:
      - admin_username
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
```
| Key | Required | Default | Description |
| --- | --- | --- | --- |
| [`certificat.authentication.type`](#certificat-authentication-type) |  | `saml` | - |
| [`certificat.authentication.administrators`](#certificat-authentication-administrators) |  | `[]` | A list of user principals who will automatically be given administrator privileges on login. |
| [`certificat.authentication.debug`](#certificat-authentication-debug) |  | `false` | The debug setting for the Django SAML plugin. |
| [`certificat.authentication.group_attribute`](#certificat-authentication-group_attribute) |  | `memberof` | The name (or translated name) of the group attribute in the returned SAML assertion |
| [`certificat.authentication.group_sync_prefix`](#certificat-authentication-group_sync_prefix) |  | `SAML/` | New groups synced from SAML will be prefixed with this identifier. |
| [`certificat.authentication.idp.local`](#certificat-authentication-idp-local) |  | `[]` | A list of local metadata files. |
| [`certificat.authentication.idp.remote`](#certificat-authentication-idp-remote) |  | `[]` | A list of remote metadata providers. |
| [`certificat.authentication.session_cookie`](#certificat-authentication-session_cookie) |  | `snickerdoodle` | The name of the session cookie. |
| [`certificat.authentication.sp.allow_unsolicited`](#certificat-authentication-sp-allow_unsolicited) |  | `true` | Allow IdP-initiated SSO. |
| [`certificat.authentication.sp.cert_file`](#certificat-authentication-sp-cert_file) | ✓ | `-` | The location of the PEM-formatted public key file |
| [`certificat.authentication.sp.digest_algorithm`](#certificat-authentication-sp-digest_algorithm) |  | `http://www.w3.org/2001/04/xmlenc#sha256` | The default digest algorithm |
| [`certificat.authentication.sp.entity_id`](#certificat-authentication-sp-entity_id) | ✓ | `-` | SAML service entity id. It should be unique and a URI. |
| [`certificat.authentication.sp.force_authn`](#certificat-authentication-sp-force_authn) |  | `false` | Disable SSO session reuse on login |
| [`certificat.authentication.sp.key_file`](#certificat-authentication-sp-key_file) | ✓ | `-` | The location of the PEM-formatted private key file |
| [`certificat.authentication.sp.name`](#certificat-authentication-sp-name) |  | `CertifiCat` | The SP name |
| [`certificat.authentication.sp.signing_algorithm`](#certificat-authentication-sp-signing_algorithm) |  | `http://www.w3.org/2001/04/xmldsig-more#rsa-sha256` | The default signing algorithm. |
| [`certificat.authentication.xmlsec_binary`](#certificat-authentication-xmlsec_binary) |  | `-` | - |

<a id="certificat-db" name="certificat-db"></a>

## `certificat.db`
This is a polymorphic property controlled by the `type` attribute. Use the following templates as an example of how to configure different `db` types.
- Required: `Yes`
- Description: Database engine settings.
- Types: [`mysql`](#certificat-db-type-mysql), [`postgresql`](#certificat-db-type-postgresql)

<a id="certificat-db-type-mysql"></a>

### `certificat.db.type: mysql`
```yaml
certificat:
  db: 
    type: "mysql"
    name: "certificat"
    user: "certificat_user"
    password: "super-s3cret-p@ssw0rd"
    host: "mariadb.my.edu"
    port: 3306
```
| Key | Required | Default | Description |
| --- | --- | --- | --- |
| [`certificat.db.type`](#certificat-db-type) |  | `mysql` | - |
| [`certificat.db.host`](#certificat-db-host) |  | `null` | Host for the database connection |
| [`certificat.db.name`](#certificat-db-name) | ✓ | `-` | The database to use after a connection is established. |
| [`certificat.db.password`](#certificat-db-password) |  | `null` | Password for the database connection |
| [`certificat.db.port`](#certificat-db-port) |  | `3306` | - |
| [`certificat.db.table_prefix`](#certificat-db-table_prefix) |  | `""` | An optional table prefix for every table in the database. |
| [`certificat.db.user`](#certificat-db-user) | ✓ | `-` | User for the database connection. |

<a id="certificat-db-type-postgresql"></a>

### `certificat.db.type: postgresql`
```yaml
certificat:
  db: 
    type: "postgresql"
    name: "certificat"
    user: "certificat_user"
    password: "super-s3cret-p@ssw0rd"
    host: "mariadb.my.edu"
    port: 3306
```
| Key | Required | Default | Description |
| --- | --- | --- | --- |
| [`certificat.db.type`](#certificat-db-type) |  | `postgresql` | - |
| [`certificat.db.host`](#certificat-db-host) |  | `null` | Host for the database connection |
| [`certificat.db.name`](#certificat-db-name) | ✓ | `-` | The database to use after a connection is established. |
| [`certificat.db.password`](#certificat-db-password) |  | `null` | Password for the database connection |
| [`certificat.db.port`](#certificat-db-port) |  | `5432` | - |
| [`certificat.db.table_prefix`](#certificat-db-table_prefix) |  | `""` | An optional table prefix for every table in the database. |
| [`certificat.db.user`](#certificat-db-user) | ✓ | `-` | User for the database connection. |

<a id="certificat-finalizer" name="certificat-finalizer"></a>

## `certificat.finalizer`
This is a polymorphic property controlled by the `type` attribute. Use the following templates as an example of how to configure different `finalizer` types.
- Required: `Yes`
- Description: Which order finalizer module to use. The server is designed to finalize all requests against one backend.
- Types: [`emsign`](#certificat-finalizer-type-emsign), [`local`](#certificat-finalizer-type-local), [`sectigo`](#certificat-finalizer-type-sectigo)

<a id="certificat-finalizer-type-emsign"></a>

### `certificat.finalizer.type: emsign`

| Key | Required | Default | Description |
| --- | --- | --- | --- |
| [`certificat.finalizer.type`](#certificat-finalizer-type) |  | `emsign` | - |
| [`certificat.finalizer.account_number`](#certificat-finalizer-account_number) | ✓ | `-` | Account number (Org. ID) |
| [`certificat.finalizer.api_base`](#certificat-finalizer-api_base) |  | `https://localhost/api/` | Base URL of the emSign API |
| [`certificat.finalizer.auth_key`](#certificat-finalizer-auth_key) | ✓ | `-` | Authorization key for API access |
| [`certificat.finalizer.poll_deadline`](#certificat-finalizer-poll_deadline) |  | `300` | The finalizer task will continue to poll the EMSign backend to check if the certificate is fulfilled until hitting this deadline in seconds. |
| [`certificat.finalizer.poll_interval`](#certificat-finalizer-poll_interval) |  | `1` | - |
| [`certificat.finalizer.prevetted_org_number`](#certificat-finalizer-prevetted_org_number) | ✓ | `-` | Pre-vetted organization id to pair with the pre-vetting token |
| [`certificat.finalizer.prevetting_token`](#certificat-finalizer-prevetting_token) | ✓ | `-` | Pre-vetting token for automatically submitting an order |
| [`certificat.finalizer.product_code`](#certificat-finalizer-product_code) | ✓ | `-` | Unique product code for the order |
| [`certificat.finalizer.requestor_email`](#certificat-finalizer-requestor_email) | ✓ | `-` | Email of the requestor |
| [`certificat.finalizer.requestor_isd_code`](#certificat-finalizer-requestor_isd_code) |  | `+1` | ISD code of the requestor |
| [`certificat.finalizer.requestor_mobile_number`](#certificat-finalizer-requestor_mobile_number) | ✓ | `-` | Mobile number of the requestor |
| [`certificat.finalizer.requestor_name`](#certificat-finalizer-requestor_name) |  | `CertifiCat` | Name of the requestor |

<a id="certificat-finalizer-type-local"></a>

### `certificat.finalizer.type: local`
```
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
```
| Key | Required | Default | Description |
| --- | --- | --- | --- |
| [`certificat.finalizer.type`](#certificat-finalizer-type) |  | `local` | - |
| [`certificat.finalizer.cert`](#certificat-finalizer-cert) | ✓ | `-` | PEM-formatted public key for the CA |
| [`certificat.finalizer.key`](#certificat-finalizer-key) | ✓ | `-` | PEM-formatted private key for the CA |

<a id="certificat-finalizer-type-sectigo"></a>

### `certificat.finalizer.type: sectigo`

| Key | Required | Default | Description |
| --- | --- | --- | --- |
| [`certificat.finalizer.type`](#certificat-finalizer-type) |  | `sectigo` | - |
| [`certificat.finalizer.api_base`](#certificat-finalizer-api_base) |  | `https://cert-manager.com/api/` | Base URL of the cert-manager API. |
| [`certificat.finalizer.api_password`](#certificat-finalizer-api_password) | ✓ | `-` | The password for the API user. |
| [`certificat.finalizer.api_user`](#certificat-finalizer-api_user) | ✓ | `-` | The API user performing the requests. |
| [`certificat.finalizer.approval_api_password`](#certificat-finalizer-approval_api_password) | ✓ | `-` | The password for the approval API user. |
| [`certificat.finalizer.approval_api_user`](#certificat-finalizer-approval_api_user) | ✓ | `-` | If your API user is unable to approve requests you will need to provide a separate user. |
| [`certificat.finalizer.cert_profile_id`](#certificat-finalizer-cert_profile_id) | ✓ | `-` | Certificate profile ID |
| [`certificat.finalizer.cert_validity_period`](#certificat-finalizer-cert_validity_period) |  | `90` | This must be set to one of the valid lifetimes for your certificate profile id. |
| [`certificat.finalizer.customer_uri`](#certificat-finalizer-customer_uri) | ✓ | `-` | Customer URI, found in the cert-manager URL. |
| [`certificat.finalizer.external_requester_override`](#certificat-finalizer-external_requester_override) |  | `null` | This email address will receive all Sectigo certificate lifecycle emails instead of the registered account email. |
| [`certificat.finalizer.org_id`](#certificat-finalizer-org_id) | ✓ | `-` | Organization or department ID |
| [`certificat.finalizer.poll_deadline`](#certificat-finalizer-poll_deadline) |  | `300` | The finalizer task will continue to poll the Sectigo backend to check if the certificate is ready for approval or approved until hitting this deadline in seconds. |
