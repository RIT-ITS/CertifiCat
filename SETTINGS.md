# Settings Documentation

| Key | Required | Default | Description |
| --- | --- | --- | --- |
| <a href="#opt-acme-authorization-client-delay" id="opt-acme-authorization-client-delay" name="opt-acme-authorization-client-delay">acme.authorization_client_delay</a>| | `15` | The Retry-After header sent to ACME clients. |
| <a href="#opt-acme-blacklisted-domains" id="opt-acme-blacklisted-domains" name="opt-acme-blacklisted-domains">acme.blacklisted_domains</a>| | `[]` | The server will refuse to issue domains for any identifiers in this list. It supports regular expressions. |
| <a href="#opt-acme-challenges-available" id="opt-acme-challenges-available" name="opt-acme-challenges-available">acme.challenges_available</a>| | `["http-01"]` | Default set of challenges created when an authorization is created |
| <a href="#opt-acme-dns-challenge-nameservers" id="opt-acme-dns-challenge-nameservers" name="opt-acme-dns-challenge-nameservers">acme.dns_challenge_nameservers</a>| | `[]` | A list of servers in the format ip or ip:port. The DNS challenge resolver will use these nameservers. If left blank the system nameservers will be used. |
| <a href="#opt-acme-eab-required" id="opt-acme-eab-required" name="opt-acme-eab-required">acme.eab_required</a>| | `false` | Whether all accounts are required to use external account binding or not. |
| <a href="#opt-acme-http-01-challenge-user-agent" id="opt-acme-http-01-challenge-user-agent" name="opt-acme-http-01-challenge-user-agent">acme.http_01_challenge_user_agent</a>| | `python-acmev2/0.2.0` | User agent the http-01 challenge validator uses when requesting the challenge document from the client server |
| <a href="#opt-acme-mask-order-processing-status-ua-match" id="opt-acme-mask-order-processing-status-ua-match" name="opt-acme-mask-order-processing-status-ua-match">acme.mask_order_processing_status_ua_match</a>| | `^cert-manager-clusterissuers.*` | Any order requests from this user agent will mask the processing state as pending |
| <a href="#opt-acme-max-identifiers" id="opt-acme-max-identifiers" name="opt-acme-max-identifiers">acme.max_identifiers</a>| | `50` | Max number of identifiers that can be passed to a new order request. |
| <a href="#opt-acme-resource-expiration-delta" id="opt-acme-resource-expiration-delta" name="opt-acme-resource-expiration-delta">acme.resource_expiration_delta</a>| | `PT8H` | How long should the order and authorization objects be valid for after generation? |
| <a href="#opt-certificat-authentication" id="opt-certificat-authentication-toplevel" name="opt-certificat-authentication-toplevel">certificat.authentication</a> ↗|✓ | `-` | Authentication settings for the web frontend. |
| <a href="#opt-certificat-beacon-enabled" id="opt-certificat-beacon-enabled" name="opt-certificat-beacon-enabled">certificat.beacon_enabled</a>| | `true` | If true, will send tracking information about usage to RIT. All tracking info is logged. |
| <a href="#opt-certificat-challenge-max-retries" id="opt-certificat-challenge-max-retries" name="opt-certificat-challenge-max-retries">certificat.challenge_max_retries</a>| | `5` | How many challenge retries to perform before marking the challenge invalid. |
| <a href="#opt-certificat-challenge-retry-delay" id="opt-certificat-challenge-retry-delay" name="opt-certificat-challenge-retry-delay">certificat.challenge_retry_delay</a>| | `2` | How long to wait between challenge retries in seconds. |
| <a href="#opt-certificat-db" id="opt-certificat-db-toplevel" name="opt-certificat-db-toplevel">certificat.db</a> ↗|✓ | `-` | Database engine settings. |
| <a href="#opt-certificat-delete-invalid-orders" id="opt-certificat-delete-invalid-orders" name="opt-certificat-delete-invalid-orders">certificat.delete_invalid_orders</a>| | `true` | If set to True, invalid orders will be purged after some time. |
| <a href="#opt-certificat-finalize-max-retries" id="opt-certificat-finalize-max-retries" name="opt-certificat-finalize-max-retries">certificat.finalize_max_retries</a>| | `10` | How many order finalization retries to perform before marking the order invalid. |
| <a href="#opt-certificat-finalize-retry-delay" id="opt-certificat-finalize-retry-delay" name="opt-certificat-finalize-retry-delay">certificat.finalize_retry_delay</a>| | `10` | How long to wait between order finalization retries in seconds. |
| <a href="#opt-certificat-finalizer" id="opt-certificat-finalizer-toplevel" name="opt-certificat-finalizer-toplevel">certificat.finalizer</a> ↗|✓ | `-` | Which order finalizer module to use. The server is designed to finalize all requests against one backend. |
| <a href="#opt-certificat-healthcheck-allowed-networks" id="opt-certificat-healthcheck-allowed-networks" name="opt-certificat-healthcheck-allowed-networks">certificat.healthcheck_allowed_networks</a>| | `["127.0.0.1/32"]` | Networks allowed to access the health endpoints. |
| <a href="#opt-certificat-hmac-id-length" id="opt-certificat-hmac-id-length" name="opt-certificat-hmac-id-length">certificat.hmac_id_length</a>| | `40` | The length of the hmac id generated for an ACME external account binding. |
| <a href="#opt-certificat-hmac-key-length" id="opt-certificat-hmac-key-length" name="opt-certificat-hmac-key-length">certificat.hmac_key_length</a>| | `90` | The length of the hmac key generated for an ACME external account binding. |
| <a href="#opt-certificat-logging-acmev2-level" id="opt-certificat-logging-acmev2-level" name="opt-certificat-logging-acmev2-level">certificat.logging.acmev2_level</a>| | `INFO` | Logging level for ACME server component. |
| <a href="#opt-certificat-logging-certificat-level" id="opt-certificat-logging-certificat-level" name="opt-certificat-logging-certificat-level">certificat.logging.certificat_level</a>| | `INFO` | Logging level for the CertifiCat frontend. |
| <a href="#opt-certificat-logging-django-level" id="opt-certificat-logging-django-level" name="opt-certificat-logging-django-level">certificat.logging.django_level</a>| | `INFO` | Logging level for Django components. |
| <a href="#opt-certificat-logging-huey-level" id="opt-certificat-logging-huey-level" name="opt-certificat-logging-huey-level">certificat.logging.huey_level</a>| | `INFO` | Logging level for the task runner. |
| <a href="#opt-certificat-logging-root-level" id="opt-certificat-logging-root-level" name="opt-certificat-logging-root-level">certificat.logging.root_level</a>| | `INFO` | Logging level for root logger. |
| <a href="#opt-certificat-redis-host" id="opt-certificat-redis-host" name="opt-certificat-redis-host">certificat.redis.host</a>|✓ | `-` | Host for the redis connection. |
| <a href="#opt-certificat-redis-password" id="opt-certificat-redis-password" name="opt-certificat-redis-password">certificat.redis.password</a>|✓ | `-` | Password for the Redis connection |
| <a href="#opt-certificat-redis-port" id="opt-certificat-redis-port" name="opt-certificat-redis-port">certificat.redis.port</a>| | `6379` | Port for the Redis connection |
| <a href="#opt-certificat-secret-key" id="opt-certificat-secret-key" name="opt-certificat-secret-key">certificat.secret_key</a>|✓ | `-` | Django SECRET_KEY. This should be set to a unique, unpredictable value. |
| <a href="#opt-certificat-session-cookie-age" id="opt-certificat-session-cookie-age" name="opt-certificat-session-cookie-age">certificat.session_cookie_age</a>| | `28800` | Django SESSION_COOKIE_AGE. This is the maximum age of the session cookie in seconds. |
| <a href="#opt-certificat-show-version" id="opt-certificat-show-version" name="opt-certificat-show-version">certificat.show_version</a>| | `false` | Show the version on the website. |
| <a href="#opt-certificat-task-queue-workers" id="opt-certificat-task-queue-workers" name="opt-certificat-task-queue-workers">certificat.task_queue.workers</a>| | `100` | Number of workers in the Huey task queue. |
| <a href="#opt-certificat-theming-global-css" id="opt-certificat-theming-global-css" name="opt-certificat-theming-global-css">certificat.theming.global_css</a>| | `null` | Global CSS injected into a style tag rendered on every page. |
| <a href="#opt-certificat-time-zone" id="opt-certificat-time-zone" name="opt-certificat-time-zone">certificat.time_zone</a>| | `America/New_York` | Django time zone, used mostly for date localization. |
| <a href="#opt-certificat-trust-proxy-forwarded-proto" id="opt-certificat-trust-proxy-forwarded-proto" name="opt-certificat-trust-proxy-forwarded-proto">certificat.trust_proxy_forwarded_proto</a>| | `false` | Signals to the app to trust the HTTP_X_FORWARDED_PROTO header if True. |
| <a href="#opt-certificat-url-root" id="opt-certificat-url-root" name="opt-certificat-url-root">certificat.url_root</a>|✓ | `-` | The url root is used to generate absolute urls to the application. It should not contain path and parameters. |

<a href="opt-certificat-authentication" id="opt-certificat-authentication" name="opt-certificat-authentication"></a>

## `certificat.authentication`
This is a polymorphic property controlled by the `type` attribute. Use the following templates as an example of how to configure different `authentication` types.
- Required: `Yes`
- Description: Authentication settings for the web frontend.
- Types: [`remote`](#opt-certificat-authentication-type-remote), [`saml`](#opt-certificat-authentication-type-saml)

<a id="opt-certificat-authentication-type-remote"></a>

### `certificat.authentication.type: remote`
```yaml
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
```
| Key | Required | Default | Description |
| --- | --- | --- | --- |
| <a href="#opt-certificat-authentication-remote-type" id="opt-certificat-authentication-remote-type" name="opt-certificat-authentication-remote-type">certificat.authentication.type</a> | | `remote` | - |
| <a href="#opt-certificat-authentication-remote-administrators" id="opt-certificat-authentication-remote-administrators" name="opt-certificat-authentication-remote-administrators">certificat.authentication.administrators</a> | | `[]` | A list of user principals who will automatically be given administrator privileges on login. |
| <a href="#opt-certificat-authentication-remote-administrators-groups" id="opt-certificat-authentication-remote-administrators-groups" name="opt-certificat-authentication-remote-administrators-groups">certificat.authentication.administrators_groups</a> | | `[]` | A list of groups that will automatically give included users administrator privileges on login. |
| <a href="#opt-certificat-authentication-remote-attribute-mapping" id="opt-certificat-authentication-remote-attribute-mapping" name="opt-certificat-authentication-remote-attribute-mapping">certificat.authentication.attribute_mapping</a> | | `{"HTTP_USER_EMAIL": "email", "HTTP_USER_FIRSTNAME": "first_name", "HTTP_USER_LASTNAME": "last_name"}` | A dictionary mapping of src:targets where attributes are mapped from headers to Django attributes. |
| <a href="#opt-certificat-authentication-remote-force-logout-if-no-header" id="opt-certificat-authentication-remote-force-logout-if-no-header" name="opt-certificat-authentication-remote-force-logout-if-no-header">certificat.authentication.force_logout_if_no_header</a> | | `true` | - |
| <a href="#opt-certificat-authentication-remote-groups-header" id="opt-certificat-authentication-remote-groups-header" name="opt-certificat-authentication-remote-groups-header">certificat.authentication.groups_header</a> | | `null` | The header that will be used to populate groups. This is delimited by the groups_header_delimiter setting. |
| <a href="#opt-certificat-authentication-remote-groups-header-delimiter" id="opt-certificat-authentication-remote-groups-header-delimiter" name="opt-certificat-authentication-remote-groups-header-delimiter">certificat.authentication.groups_header_delimiter</a> | | `;` | The delimiter used when parsing the groups_header value. |
| <a href="#opt-certificat-authentication-remote-log-http-headers" id="opt-certificat-authentication-remote-log-http-headers" name="opt-certificat-authentication-remote-log-http-headers">certificat.authentication.log_http_headers</a> | | `false` | - |
| <a href="#opt-certificat-authentication-remote-redirect-template" id="opt-certificat-authentication-remote-redirect-template" name="opt-certificat-authentication-remote-redirect-template">certificat.authentication.redirect_template</a> |✓ | `-` | Templated URL target for redirects. The redirect variable is substituted with the URL encoded path of the protected resource. |
| <a href="#opt-certificat-authentication-remote-user-header" id="opt-certificat-authentication-remote-user-header" name="opt-certificat-authentication-remote-user-header">certificat.authentication.user_header</a> | | `HTTP_USER` | The header that will be used to populate user principal. |

<a id="opt-certificat-authentication-type-saml"></a>

### `certificat.authentication.type: saml`
```yaml
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
```
| Key | Required | Default | Description |
| --- | --- | --- | --- |
| <a href="#opt-certificat-authentication-saml-type" id="opt-certificat-authentication-saml-type" name="opt-certificat-authentication-saml-type">certificat.authentication.type</a> | | `saml` | - |
| <a href="#opt-certificat-authentication-saml-administrators" id="opt-certificat-authentication-saml-administrators" name="opt-certificat-authentication-saml-administrators">certificat.authentication.administrators</a> | | `[]` | A list of user principals who will automatically be given administrator privileges on login. |
| <a href="#opt-certificat-authentication-saml-administrators-groups" id="opt-certificat-authentication-saml-administrators-groups" name="opt-certificat-authentication-saml-administrators-groups">certificat.authentication.administrators_groups</a> | | `[]` | A list of groups that will automatically give administrator privileges to any included users on login. |
| <a href="#opt-certificat-authentication-saml-attribute-mapping" id="opt-certificat-authentication-saml-attribute-mapping" name="opt-certificat-authentication-saml-attribute-mapping">certificat.authentication.attribute_mapping</a> | | `{"eduPersonPrincipalName": ["username"], "eduPersonTargetedID": ["username"], "givenName": ["first_name"], "mail": ["email"], "sn": ["last_name"], "uid": ["username"]}` | A dictionary mapping of src:[target] where attributes are mapped from SAML responses to Django attributes. This is designed to work with a yaml config, not environment variables. |
| <a href="#opt-certificat-authentication-saml-debug" id="opt-certificat-authentication-saml-debug" name="opt-certificat-authentication-saml-debug">certificat.authentication.debug</a> | | `false` | The debug setting for the Django SAML plugin. |
| <a href="#opt-certificat-authentication-saml-group-attribute" id="opt-certificat-authentication-saml-group-attribute" name="opt-certificat-authentication-saml-group-attribute">certificat.authentication.group_attribute</a> | | `memberof` | The name (or translated name) of the group attribute in the returned SAML assertion |
| <a href="#opt-certificat-authentication-saml-group-sync-prefix" id="opt-certificat-authentication-saml-group-sync-prefix" name="opt-certificat-authentication-saml-group-sync-prefix">certificat.authentication.group_sync_prefix</a> | | `SAML/` | New groups synced from SAML will be prefixed with this identifier. |
| <a href="#opt-certificat-authentication-saml-idp" id="opt-certificat-authentication-saml-idp" name="opt-certificat-authentication-saml-idp">certificat.authentication.idp</a> |✓ | `-` | - |
| <a href="#opt-certificat-authentication-saml-idp-local" id="opt-certificat-authentication-saml-idp-local" name="opt-certificat-authentication-saml-idp-local">certificat.authentication.idp.local</a> | | `[]` | A list of local metadata files. |
| <a href="#opt-certificat-authentication-saml-idp-remote" id="opt-certificat-authentication-saml-idp-remote" name="opt-certificat-authentication-saml-idp-remote">certificat.authentication.idp.remote</a> | | `[]` | A list of remote metadata providers. |
| <a href="#opt-certificat-authentication-saml-session-cookie" id="opt-certificat-authentication-saml-session-cookie" name="opt-certificat-authentication-saml-session-cookie">certificat.authentication.session_cookie</a> | | `snickerdoodle` | The name of the session cookie. |
| <a href="#opt-certificat-authentication-saml-sp" id="opt-certificat-authentication-saml-sp" name="opt-certificat-authentication-saml-sp">certificat.authentication.sp</a> |✓ | `-` | - |
| <a href="#opt-certificat-authentication-saml-sp-allow-unsolicited" id="opt-certificat-authentication-saml-sp-allow-unsolicited" name="opt-certificat-authentication-saml-sp-allow-unsolicited">certificat.authentication.sp.allow_unsolicited</a> | | `true` | Allow IdP-initiated SSO. |
| <a href="#opt-certificat-authentication-saml-sp-cert-file" id="opt-certificat-authentication-saml-sp-cert-file" name="opt-certificat-authentication-saml-sp-cert-file">certificat.authentication.sp.cert_file</a> |✓ | `-` | The location of the PEM-formatted public key file |
| <a href="#opt-certificat-authentication-saml-sp-digest-algorithm" id="opt-certificat-authentication-saml-sp-digest-algorithm" name="opt-certificat-authentication-saml-sp-digest-algorithm">certificat.authentication.sp.digest_algorithm</a> | | `http://www.w3.org/2001/04/xmlenc#sha256` | The default digest algorithm |
| <a href="#opt-certificat-authentication-saml-sp-entity-id" id="opt-certificat-authentication-saml-sp-entity-id" name="opt-certificat-authentication-saml-sp-entity-id">certificat.authentication.sp.entity_id</a> |✓ | `-` | SAML service entity id. It should be unique and a URI. |
| <a href="#opt-certificat-authentication-saml-sp-force-authn" id="opt-certificat-authentication-saml-sp-force-authn" name="opt-certificat-authentication-saml-sp-force-authn">certificat.authentication.sp.force_authn</a> | | `false` | Disable SSO session reuse on login |
| <a href="#opt-certificat-authentication-saml-sp-key-file" id="opt-certificat-authentication-saml-sp-key-file" name="opt-certificat-authentication-saml-sp-key-file">certificat.authentication.sp.key_file</a> |✓ | `-` | The location of the PEM-formatted private key file |
| <a href="#opt-certificat-authentication-saml-sp-name" id="opt-certificat-authentication-saml-sp-name" name="opt-certificat-authentication-saml-sp-name">certificat.authentication.sp.name</a> | | `CertifiCat` | The SP name |
| <a href="#opt-certificat-authentication-saml-sp-signing-algorithm" id="opt-certificat-authentication-saml-sp-signing-algorithm" name="opt-certificat-authentication-saml-sp-signing-algorithm">certificat.authentication.sp.signing_algorithm</a> | | `http://www.w3.org/2001/04/xmldsig-more#rsa-sha256` | The default signing algorithm. |

<a href="opt-certificat-db" id="opt-certificat-db" name="opt-certificat-db"></a>

## `certificat.db`
This is a polymorphic property controlled by the `type` attribute. Use the following templates as an example of how to configure different `db` types.
- Required: `Yes`
- Description: Database engine settings.
- Types: [`mysql`](#opt-certificat-db-type-mysql), [`postgresql`](#opt-certificat-db-type-postgresql)

<a id="opt-certificat-db-type-mysql"></a>

### `certificat.db.type: mysql`
```yaml
certificat:
  db: 
    type: "mysql"
    host: "mariadb.my.edu"
    name: "certificat"
    user: "certificat_user"
    password: "super-s3cret-p@ssw0rd"
```
| Key | Required | Default | Description |
| --- | --- | --- | --- |
| <a href="#opt-certificat-db-mysql-type" id="opt-certificat-db-mysql-type" name="opt-certificat-db-mysql-type">certificat.db.type</a> | | `mysql` | - |
| <a href="#opt-certificat-db-mysql-host" id="opt-certificat-db-mysql-host" name="opt-certificat-db-mysql-host">certificat.db.host</a> | | `null` | Host for the database connection |
| <a href="#opt-certificat-db-mysql-name" id="opt-certificat-db-mysql-name" name="opt-certificat-db-mysql-name">certificat.db.name</a> |✓ | `-` | The database to use after a connection is established. |
| <a href="#opt-certificat-db-mysql-options" id="opt-certificat-db-mysql-options" name="opt-certificat-db-mysql-options">certificat.db.options</a> | | `{}` | Key-value options passed to the driver |
| <a href="#opt-certificat-db-mysql-password" id="opt-certificat-db-mysql-password" name="opt-certificat-db-mysql-password">certificat.db.password</a> | | `null` | Password for the database connection |
| <a href="#opt-certificat-db-mysql-port" id="opt-certificat-db-mysql-port" name="opt-certificat-db-mysql-port">certificat.db.port</a> | | `3306` | - |
| <a href="#opt-certificat-db-mysql-user" id="opt-certificat-db-mysql-user" name="opt-certificat-db-mysql-user">certificat.db.user</a> |✓ | `-` | User for the database connection. |

<a id="opt-certificat-db-type-postgresql"></a>

### `certificat.db.type: postgresql`
```yaml
certificat:
  db: 
    type: "postgresql"
    host: "postgres.my.edu"
    name: "certificat"
    user: "certificat_user"
    password: "super-s3cret-p@ssw0rd"
```
| Key | Required | Default | Description |
| --- | --- | --- | --- |
| <a href="#opt-certificat-db-postgresql-type" id="opt-certificat-db-postgresql-type" name="opt-certificat-db-postgresql-type">certificat.db.type</a> | | `postgresql` | - |
| <a href="#opt-certificat-db-postgresql-host" id="opt-certificat-db-postgresql-host" name="opt-certificat-db-postgresql-host">certificat.db.host</a> | | `null` | Host for the database connection |
| <a href="#opt-certificat-db-postgresql-name" id="opt-certificat-db-postgresql-name" name="opt-certificat-db-postgresql-name">certificat.db.name</a> |✓ | `-` | The database to use after a connection is established. |
| <a href="#opt-certificat-db-postgresql-options" id="opt-certificat-db-postgresql-options" name="opt-certificat-db-postgresql-options">certificat.db.options</a> | | `{}` | Key-value options passed to the driver |
| <a href="#opt-certificat-db-postgresql-password" id="opt-certificat-db-postgresql-password" name="opt-certificat-db-postgresql-password">certificat.db.password</a> | | `null` | Password for the database connection |
| <a href="#opt-certificat-db-postgresql-port" id="opt-certificat-db-postgresql-port" name="opt-certificat-db-postgresql-port">certificat.db.port</a> | | `5432` | - |
| <a href="#opt-certificat-db-postgresql-user" id="opt-certificat-db-postgresql-user" name="opt-certificat-db-postgresql-user">certificat.db.user</a> |✓ | `-` | User for the database connection. |

<a href="opt-certificat-finalizer" id="opt-certificat-finalizer" name="opt-certificat-finalizer"></a>

## `certificat.finalizer`
This is a polymorphic property controlled by the `type` attribute. Use the following templates as an example of how to configure different `finalizer` types.
- Required: `Yes`
- Description: Which order finalizer module to use. The server is designed to finalize all requests against one backend.
- Types: [`acme`](#opt-certificat-finalizer-type-acme), [`certinext`](#opt-certificat-finalizer-type-certinext), [`local`](#opt-certificat-finalizer-type-local), [`sectigo`](#opt-certificat-finalizer-type-sectigo)

<a id="opt-certificat-finalizer-type-acme"></a>

### `certificat.finalizer.type: acme`

| Key | Required | Default | Description |
| --- | --- | --- | --- |
| <a href="#opt-certificat-finalizer-acme-type" id="opt-certificat-finalizer-acme-type" name="opt-certificat-finalizer-acme-type">certificat.finalizer.type</a> | | `acme` | - |
| <a href="#opt-certificat-finalizer-acme-account-email" id="opt-certificat-finalizer-acme-account-email" name="opt-certificat-finalizer-acme-account-email">certificat.finalizer.account_email</a> |✓ | `-` | Email address used as a contact when binding an account. |
| <a href="#opt-certificat-finalizer-acme-account-hmac-key" id="opt-certificat-finalizer-acme-account-hmac-key" name="opt-certificat-finalizer-acme-account-hmac-key">certificat.finalizer.account_hmac_key</a> |✓ | `-` | External account binding HMAC key. |
| <a href="#opt-certificat-finalizer-acme-account-kid" id="opt-certificat-finalizer-acme-account-kid" name="opt-certificat-finalizer-acme-account-kid">certificat.finalizer.account_kid</a> |✓ | `-` | External account binding key identifier. |
| <a href="#opt-certificat-finalizer-acme-directory" id="opt-certificat-finalizer-acme-directory" name="opt-certificat-finalizer-acme-directory">certificat.finalizer.directory</a> |✓ | `-` | Path to the ACME API endpoint. This usually ends with /directory. |
| <a href="#opt-certificat-finalizer-acme-finalization-timeout" id="opt-certificat-finalizer-acme-finalization-timeout" name="opt-certificat-finalizer-acme-finalization-timeout">certificat.finalizer.finalization_timeout</a> | | `90` | How long to poll the upstream server before finalization is canceled. |
| <a href="#opt-certificat-finalizer-acme-skip-answering-challenges" id="opt-certificat-finalizer-acme-skip-answering-challenges" name="opt-certificat-finalizer-acme-skip-answering-challenges">certificat.finalizer.skip_answering_challenges</a> | | `false` | Skip answering authorization challenges. This may be used if the upstream ACME server supports pre-authorization. |

<a id="opt-certificat-finalizer-type-certinext"></a>

### `certificat.finalizer.type: certinext`

| Key | Required | Default | Description |
| --- | --- | --- | --- |
| <a href="#opt-certificat-finalizer-certinext-type" id="opt-certificat-finalizer-certinext-type" name="opt-certificat-finalizer-certinext-type">certificat.finalizer.type</a> | | `certinext` | - |
| <a href="#opt-certificat-finalizer-certinext-account-number" id="opt-certificat-finalizer-certinext-account-number" name="opt-certificat-finalizer-certinext-account-number">certificat.finalizer.account_number</a> |✓ | `-` | Account number (Org. ID) |
| <a href="#opt-certificat-finalizer-certinext-api-base" id="opt-certificat-finalizer-certinext-api-base" name="opt-certificat-finalizer-certinext-api-base">certificat.finalizer.api_base</a> | | `https://localhost/api/` | Base URL of the CERTInext API |
| <a href="#opt-certificat-finalizer-certinext-auth-key" id="opt-certificat-finalizer-certinext-auth-key" name="opt-certificat-finalizer-certinext-auth-key">certificat.finalizer.auth_key</a> |✓ | `-` | Authorization key for API access |
| <a href="#opt-certificat-finalizer-certinext-poll-deadline" id="opt-certificat-finalizer-certinext-poll-deadline" name="opt-certificat-finalizer-certinext-poll-deadline">certificat.finalizer.poll_deadline</a> | | `300` | The finalizer task will continue to poll the CertiNext backend to check if the certificate is fulfilled until hitting this deadline in seconds. |
| <a href="#opt-certificat-finalizer-certinext-poll-interval" id="opt-certificat-finalizer-certinext-poll-interval" name="opt-certificat-finalizer-certinext-poll-interval">certificat.finalizer.poll_interval</a> | | `1` | - |
| <a href="#opt-certificat-finalizer-certinext-prevetted-org-number" id="opt-certificat-finalizer-certinext-prevetted-org-number" name="opt-certificat-finalizer-certinext-prevetted-org-number">certificat.finalizer.prevetted_org_number</a> |✓ | `-` | Pre-vetted organization id to pair with the pre-vetting token |
| <a href="#opt-certificat-finalizer-certinext-prevetting-token" id="opt-certificat-finalizer-certinext-prevetting-token" name="opt-certificat-finalizer-certinext-prevetting-token">certificat.finalizer.prevetting_token</a> |✓ | `-` | Pre-vetting token for automatically submitting an order |
| <a href="#opt-certificat-finalizer-certinext-product-code" id="opt-certificat-finalizer-certinext-product-code" name="opt-certificat-finalizer-certinext-product-code">certificat.finalizer.product_code</a> |✓ | `-` | Unique product code for the order |
| <a href="#opt-certificat-finalizer-certinext-requestor-email" id="opt-certificat-finalizer-certinext-requestor-email" name="opt-certificat-finalizer-certinext-requestor-email">certificat.finalizer.requestor_email</a> |✓ | `-` | Email of the requestor |
| <a href="#opt-certificat-finalizer-certinext-requestor-isd-code" id="opt-certificat-finalizer-certinext-requestor-isd-code" name="opt-certificat-finalizer-certinext-requestor-isd-code">certificat.finalizer.requestor_isd_code</a> | | `+1` | ISD code of the requestor |
| <a href="#opt-certificat-finalizer-certinext-requestor-mobile-number" id="opt-certificat-finalizer-certinext-requestor-mobile-number" name="opt-certificat-finalizer-certinext-requestor-mobile-number">certificat.finalizer.requestor_mobile_number</a> |✓ | `-` | Mobile number of the requestor |
| <a href="#opt-certificat-finalizer-certinext-requestor-name" id="opt-certificat-finalizer-certinext-requestor-name" name="opt-certificat-finalizer-certinext-requestor-name">certificat.finalizer.requestor_name</a> | | `CertifiCat` | Name of the requestor |

<a id="opt-certificat-finalizer-type-local"></a>

### `certificat.finalizer.type: local`
```yaml
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
| <a href="#opt-certificat-finalizer-local-type" id="opt-certificat-finalizer-local-type" name="opt-certificat-finalizer-local-type">certificat.finalizer.type</a> | | `local` | - |
| <a href="#opt-certificat-finalizer-local-cert" id="opt-certificat-finalizer-local-cert" name="opt-certificat-finalizer-local-cert">certificat.finalizer.cert</a> |✓ | `-` | PEM-formatted public key for the CA |
| <a href="#opt-certificat-finalizer-local-key" id="opt-certificat-finalizer-local-key" name="opt-certificat-finalizer-local-key">certificat.finalizer.key</a> |✓ | `-` | PEM-formatted private key for the CA |

<a id="opt-certificat-finalizer-type-sectigo"></a>

### `certificat.finalizer.type: sectigo`

| Key | Required | Default | Description |
| --- | --- | --- | --- |
| <a href="#opt-certificat-finalizer-sectigo-type" id="opt-certificat-finalizer-sectigo-type" name="opt-certificat-finalizer-sectigo-type">certificat.finalizer.type</a> | | `sectigo` | - |
| <a href="#opt-certificat-finalizer-sectigo-api-base" id="opt-certificat-finalizer-sectigo-api-base" name="opt-certificat-finalizer-sectigo-api-base">certificat.finalizer.api_base</a> | | `https://cert-manager.com/api/` | Base URL of the cert-manager API. |
| <a href="#opt-certificat-finalizer-sectigo-api-password" id="opt-certificat-finalizer-sectigo-api-password" name="opt-certificat-finalizer-sectigo-api-password">certificat.finalizer.api_password</a> |✓ | `-` | The password for the API user. |
| <a href="#opt-certificat-finalizer-sectigo-api-user" id="opt-certificat-finalizer-sectigo-api-user" name="opt-certificat-finalizer-sectigo-api-user">certificat.finalizer.api_user</a> |✓ | `-` | The API user performing the requests. |
| <a href="#opt-certificat-finalizer-sectigo-approval-api-password" id="opt-certificat-finalizer-sectigo-approval-api-password" name="opt-certificat-finalizer-sectigo-approval-api-password">certificat.finalizer.approval_api_password</a> |✓ | `-` | The password for the approval API user. |
| <a href="#opt-certificat-finalizer-sectigo-approval-api-user" id="opt-certificat-finalizer-sectigo-approval-api-user" name="opt-certificat-finalizer-sectigo-approval-api-user">certificat.finalizer.approval_api_user</a> |✓ | `-` | If your API user is unable to approve requests you will need to provide a separate user. |
| <a href="#opt-certificat-finalizer-sectigo-cert-profile-id" id="opt-certificat-finalizer-sectigo-cert-profile-id" name="opt-certificat-finalizer-sectigo-cert-profile-id">certificat.finalizer.cert_profile_id</a> |✓ | `-` | Certificate profile ID |
| <a href="#opt-certificat-finalizer-sectigo-cert-validity-period" id="opt-certificat-finalizer-sectigo-cert-validity-period" name="opt-certificat-finalizer-sectigo-cert-validity-period">certificat.finalizer.cert_validity_period</a> | | `90` | This must be set to one of the valid lifetimes for your certificate profile id. |
| <a href="#opt-certificat-finalizer-sectigo-customer-uri" id="opt-certificat-finalizer-sectigo-customer-uri" name="opt-certificat-finalizer-sectigo-customer-uri">certificat.finalizer.customer_uri</a> |✓ | `-` | Customer URI, found in the cert-manager URL. |
| <a href="#opt-certificat-finalizer-sectigo-external-requester-override" id="opt-certificat-finalizer-sectigo-external-requester-override" name="opt-certificat-finalizer-sectigo-external-requester-override">certificat.finalizer.external_requester_override</a> | | `null` | This email address will receive all Sectigo certificate lifecycle emails instead of the registered account email. |
| <a href="#opt-certificat-finalizer-sectigo-org-id" id="opt-certificat-finalizer-sectigo-org-id" name="opt-certificat-finalizer-sectigo-org-id">certificat.finalizer.org_id</a> |✓ | `-` | Organization or department ID |
| <a href="#opt-certificat-finalizer-sectigo-poll-deadline" id="opt-certificat-finalizer-sectigo-poll-deadline" name="opt-certificat-finalizer-sectigo-poll-deadline">certificat.finalizer.poll_deadline</a> | | `300` | The finalizer task will continue to poll the Sectigo backend to check if the certificate is ready for approval or approved until hitting this deadline in seconds. |
