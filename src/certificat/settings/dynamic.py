import multiprocessing
import os
import re
import textwrap
from collections.abc import Mapping
from typing import ClassVar, Literal, Self

import inject
import peewee
import yaml
from acmev2.settings import ACMESettings
from pydantic import BaseModel, Field, HttpUrl, ValidationError, field_validator
from pydantic.json_schema import SkipJsonSchema
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

BetaFeature = SkipJsonSchema


class Settings(BaseSettings):
    pass


class DatabaseSettings(BaseModel):
    type: SkipJsonSchema[Literal["none"]] = "None"

    def to_peewee(self) -> peewee.Database:
        return "sqlite:///huey-stats.db.sqlite3"

    def to_backend(self) -> dict:
        raise Exception("Database settings were not configured.")  # noqa: TRY002


class MariaDBDatabaseSettings(DatabaseSettings):
    type: SkipJsonSchema[Literal["mysql"]] = "mysql"
    engine: SkipJsonSchema[str] = "django.db.backends.mysql"
    name: str = Field(
        description="The database to use after a connection is established."
    )
    user: str = Field(description="User for the database connection.")
    password: str = Field(None, description="Password for the database connection.")
    host: str = Field(None, description="Host for the database connection.")
    port: int = Field(3306, description="Port for the database connection.")
    options: dict = Field({}, description="Key-value options passed to the driver.")
    table_prefix: SkipJsonSchema[str] = Field(
        "",
        description="An optional table prefix for every table in the database.",
        deprecated="This option is deprecated and is not supported for future development. It may be removed at any time.",
    )

    def to_peewee(self) -> peewee.MySQLDatabase:
        return peewee.MySQLDatabase(
            self.name,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            ssl=self.options.get("ssl"),
        )

    def to_backend(self) -> dict:
        return {
            "ENGINE": self.engine,
            "NAME": self.name,
            "USER": self.user,
            "PASSWORD": self.password,
            "HOST": self.host,
            "PORT": self.port,
            "OPTIONS": self.options,
        }


class PostgresDatabaseSettings(DatabaseSettings):
    type: SkipJsonSchema[Literal["postgresql"]] = "postgresql"
    engine: SkipJsonSchema[str] = "django.db.backends.postgresql"
    name: str = Field(
        description="The database to use after a connection is established."
    )
    user: str = Field(description="User for the database connection.")
    password: str = Field(None, description="Password for the database connection.")
    host: str = Field(None, description="Host for the database connection.")
    port: int = Field(5432, description="Port for the database connection.")
    options: dict = Field({}, description="Key-value options passed to the driver.")
    table_prefix: SkipJsonSchema[str] = Field(
        "", description="An optional table prefix for every table in the database."
    )

    def to_backend(self) -> dict:
        return {
            "ENGINE": self.engine,
            "NAME": self.name,
            "USER": self.user,
            "PASSWORD": self.password,
            "HOST": self.host,
            "PORT": self.port,
            "OPTIONS": self.options,
        }


class SQLiteDatabaseSettings(DatabaseSettings):
    type: SkipJsonSchema[Literal["sqlite"]] = "sqlite"
    engine: SkipJsonSchema[str] = "django.db.backends.sqlite3"
    name: str = Field(description="The location of the sqlite database.")
    options: dict = Field({}, description="Key-value options passed to the driver")

    def to_backend(self) -> dict:
        return {
            "ENGINE": self.engine,
            "NAME": self.name,
            "OPTIONS": self.options,
        }


class TaskQueueSettings(BaseModel):
    workers: int = Field(
        max(5, min(multiprocessing.cpu_count() * 5, 20)),
        description="Number of workers in the Huey task queue.",
    )
    stats_database: str | None = Field(
        None,
        description="Location of the stats database. This is a connection string.",
        examples=["`sqlite:///huey-stats.db`"],
    )


class CacheSettings(BaseModel):
    type: SkipJsonSchema[Literal["django.core.cache.backends.None"]] = (
        "django.core.cache.backends.None"
    )

    def to_backend(self):
        raise Exception("Cache settings were not configured.")  # noqa: TRY002


class RedisCacheSettings(CacheSettings):
    type: SkipJsonSchema[Literal["redis"]] = "redis"
    backend: str = "django.core.cache.backends.redis.RedisCache"

    def to_backend(self):
        redis_settings = inject.instance(ApplicationSettings).redis
        return {
            "BACKEND": self.backend,
            "LOCATION": f"redis://:{redis_settings.password}@{redis_settings.host}:{redis_settings.port}",
            "OPTIONS": {"health_check_interval": 30},
        }


class LocalMemoryCacheSettings(CacheSettings):
    type: SkipJsonSchema[Literal["local"]] = "local"
    backend: str = "django.core.cache.backends.locmem.LocMemCache"

    def to_backend(self):
        return {"BACKEND": self.backend}


class RedisSettings(BaseModel):
    backend: SkipJsonSchema[Literal["django.core.cache.backends.redis.RedisCache"]] = (
        "django.core.cache.backends.redis.RedisCache"
    )
    host: str = Field(description="Host for the Redis connection.")
    password: str = Field(description="Password for the Redis connection.")
    port: int = Field(6379, description="Port for the Redis connection.")


class LoggingSettings(BaseModel):
    certificat_level: str | None = Field(
        "INFO", description="Logging level for the CertifiCat frontend."
    )
    huey_level: str | None = Field(
        "INFO", description="Logging level for the task runner."
    )
    django_level: str | None = Field(
        "INFO", description="Logging level for Django components."
    )
    acmev2_level: str | None = Field(
        "INFO", description="Logging level for ACME server component."
    )
    root_level: str | None = Field("INFO", description="Logging level for root logger.")


class ThemeSettings(BaseModel):
    global_css: str | None = Field(
        None,
        description=textwrap.dedent("""
            Global CSS injected into a style tag rendered on every page. For example the following section configures the site to use RIT branding:

            !!! example

                ```yaml
                certificat:
                  theming:
                    global_css: |
                      html:root {
                        --primary-color: #F76902;
                        --link-color: #C75300;
                        --logo-accent-color: #F76902;
                        --neutral-cool-color--100: #D0D3D4;
                        --neutral-cool-color--200: #A2AAAD;
                        --neutral-cool-color--300: #7C878E;
                        --neutral-warm-color--100: #D7D2CB;
                        --neutral-warm-color--200: #ACA39A;
                        --green-accent-color: #84BD00;
                        --lime-accent-color: #C4D600;
                        --blue-accent-color: #009CBD;
                        --purple-accent-color: #7D55C7;
                        --red-accent-color: #DA291C;
                        --orange-accent-color: #F6BE00;
                        --gray-color--100: #f8f9fa;
                        --gray-color--200: #e9ecef;
                        --gray-color--300: #dee2e6;
                        --gray-color--400: #ced4da;
                        --gray-color--500: #adb5bd;
                        --gray-color--600: #6c757d;
                        --gray-color--700: #495057;
                        --gray-color--800: #343a40;
                        --gray-color--900: #212529;
                        --body-text-color: #212529;
                        --font-stack: Helvetica Neue, Helvetica, Arial, sans‑serif;
                        
                        --width--small-smartphone: 480px;
                        --width--large-smartphone: 768px;
                        --width--tiny-desktop: 1000px;
                        --width--small-desktop: 1200px;
                        --width--max: 1400px;
                        
                        --font-size: 16px;
                      }

                      activity-graph {
                        --heat-calendar--start-color: #cff182 !important;
                        --heat-calendar--end-color: #fff8a4 !important;
                      }
                ```
        """),
    )


class SAMLSPSettings(BaseModel):
    entity_id: str = Field(
        description="SAML service entity id. It should be unique and a URI."
    )
    name: str = Field("CertifiCat", description="The SP name in generated metadata.")
    key_file: str = Field(
        description="The location of the PEM-formatted private key file."
    )
    cert_file: str = Field(
        description="The location of the PEM-formatted public key file."
    )
    signing_algorithm: str = Field(
        "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
        description="The default signing algorithm.",
    )
    digest_algorithm: str = Field(
        "http://www.w3.org/2001/04/xmlenc#sha256",
        description="The default digest algorithm",
    )
    force_authn: bool = Field(False, description="Disable SSO session reuse on login.")
    allow_unsolicited: bool = Field(True, description="Allow IdP-initiated SSO.")


class RemoteIdP(BaseModel):
    url: str = Field(description="IdP metadata URL.")
    cert: str | None = Field(
        None, required=False, description="Signing certificate for the remote metadata."
    )


class MDQ(BaseModel):
    url: str = Field(description="Metadata query URL.")
    cert: str | None = Field(
        None,
        required=False,
        description="Signing certificate for the metadata query URL.",
    )
    freshness_period: str = "P0Y0M0DT2H0M0S"


class SAMLIdPSettings(BaseModel):
    local: list[str] = Field([], description="A list of local metadata files.")
    remote: list[RemoteIdP] = Field(
        [], description="A list of remote metadata providers.", required=False
    )
    mdq: SkipJsonSchema[list[MDQ]] = Field(
        [], description="A list of metadata query providers.", required=False
    )


class SAMLDiscoverySettings(BaseModel):
    service: str = Field(
        description="SAML discovery service. This feature is experimental and subject to change."
    )
    response: list[str] = Field(
        [],
        description="Discovery response endpoints. This feature is experimental and subject to change.",
    )


class LocalAuthAdminSettings(BaseModel):
    username: str
    password: str
    email: str


class LocalAuthSettings(BaseModel):
    type: SkipJsonSchema[Literal["local"]] = "local"
    admin: LocalAuthAdminSettings


class RemoteAuthSettings(BaseModel):
    type: SkipJsonSchema[Literal["remote"]] = "remote"
    user_header: str = Field(
        "HTTP_USER",
        description="The header that will be used to populate user principal.",
    )
    groups_header: str | None = Field(
        None,
        description="The header that will be used to populate groups. This is delimited by the groups_header_delimiter setting.",
        examples=["`HTTP_GROUPS`"],
    )
    groups_header_delimiter: str = Field(
        ";", description="The delimiter used when parsing the groups_header value."
    )
    group_sync_prefix: SkipJsonSchema[str] = Field(
        "REMOTE/",
        description="New groups synced from remote auth will be prefixed with this identifier.",
    )

    administrators: list[str] = Field(
        [],
        description="A list of user principals who will automatically be given administrator privileges on login.",
    )
    administrators_groups: list[str] = Field(
        [],
        description="A list of groups that will automatically give included users administrator privileges on login.",
    )
    force_logout_if_no_header: bool = Field(
        True,
        description="Destroys the user session if the remote header is not present. This should be turned off if the header is not transmitted with every request.",
    )
    log_http_headers: bool = Field(
        False,
        description="Adds header debugging to the web logs. Useful when debugging why user authentication is not behaving as expected.",
    )
    attribute_mapping: Mapping[str, list[str] | str] = Field(
        {
            "HTTP_USER_EMAIL": "email",
            "HTTP_USER_FIRSTNAME": "first_name",
            "HTTP_USER_LASTNAME": "last_name",
        },
        description="A dictionary mapping of src:targets where attributes are mapped from headers to Django attributes.",
    )
    redirect_template: str = Field(
        description=textwrap.dedent("""
            Templated URL target for redirects. The redirect variable is substituted with the URL encoded path of the protected resource instead of the user returning to the root. This allows you to deep-link back to the protected resource.

            For example, if a user attempted to access the protected resource `https://acme.edu/accounts/` and the authorization server lived at `https://auth.acme.edu/` 
            you could set the redirect_template to `https://auth.acme.edu/?redirect_to={{ redirect }}`.

            CertifiCat would redirect the request to `https://auth.acme.edu/?redirect_to=https%3A%2F%2Facme.edu%2Faccounts%2F`.
        """)
    )


class SAMLAuthSettings(BaseModel):
    type: SkipJsonSchema[Literal["saml"]] = "saml"
    model_config = SettingsConfigDict(
        validate_default=False,
        env_prefix="SAML__",
        from_attributes=True,
        env_nested_delimiter="__",
    )

    @classmethod
    def get(cls) -> Self:
        settings = inject.instance(ApplicationSettings)
        if settings.authentication.type == "saml":
            return settings.authentication

    debug: bool = Field(
        False,
        description="The debug setting for the Django SAML plugin. This increases log verbosity.",
    )
    xmlsec_binary: SkipJsonSchema[str] = Field(
        "/usr/bin/xmlsec1", description="The absolute path to the xmlsec binary."
    )

    session_cookie: str = Field(
        "snickerdoodle", description="The name of the session cookie."
    )
    administrators: list[str] = Field(
        [],
        description="A list of user principals who will automatically be given administrator privileges on login.",
    )
    administrators_groups: list[str] = Field(
        [],
        description="A list of groups that will automatically give administrator privileges to any included users on login.",
    )

    group_attribute: str = Field(
        "memberof",
        description="The name (or translated name) of the group attribute in the returned SAML assertion",
    )
    group_sync_prefix: str = Field(
        "SAML/",
        description="New groups synced from SAML will be prefixed with this identifier. Generally leave this setting as the default.",
    )

    sp: SAMLSPSettings
    idp: SAMLIdPSettings
    discovery: SkipJsonSchema[SAMLDiscoverySettings | None] = None

    attribute_mapping: Mapping[str, list[str]] = Field(
        {
            "uid": ["username"],
            "eduPersonPrincipalName": ["username"],
            "eduPersonTargetedID": ["username"],
            "mail": ["email"],
            "givenName": ["first_name"],
            "sn": ["last_name"],
        },
        description=textwrap.dedent("""
            A dictionary mapping of src:[target] where attributes are mapped from SAML responses to Django attributes.

            The default mapping is a best-effort guess at how attributes may flow from the IdP to the CertifiCat service. Depending on attribute naming
            you may need to adjust these. For example, consider an IdP that sends the `urn:oid:0.9.2342.19200300.100.1.1` attribute for uid and the `urn:oid:0.9.2342.19200300.100.1.3` attribute for mail.

            ```yaml
            certificat:
              authentication:
                attribute_mapping:
                  "urn:oid:0.9.2342.19200300.100.1.1": ["username"]
                  "urn:oid:0.9.2342.19200300.100.1.3": ["mail"]
                  ...
            ```
        """),
    )


class FinalizerSettings(BaseModel):
    type: SkipJsonSchema[Literal["none"]] = "none"
    module: str


class WebhookSettings(BaseModel):
    secret: str = Field(
        description="Shared secret used to generate webhook signatures. This should be between 24 and 64 bytes."
    )
    endpoint: HttpUrl = Field(description="URL to send the webhook request.")
    timeout: int = Field(5, description="Request timeout for the endpoint URL.")


class ACMEFinalizerDNS01ChallengeSettings(BaseModel):
    perform_verification: bool = Field(
        False,
        description="Verify DNS TXT records for challenges before submitting the order.",
    )
    verification_nameservers: list[str] = Field(
        ["1.1.1.1"],
        description="A list of servers in the format ip or ip:port. The resolver will use these nameservers when verifying challenges. If left blank the system nameservers will be used.",
    )
    verification_timeout: int = Field(
        60,
        description="Timeout for challenge verification in seconds, after which the order will be marked invalid.",
    )


class ACMEFinalizerChallengeSettings(BaseModel):
    dns_01: ACMEFinalizerDNS01ChallengeSettings = Field(
        ACMEFinalizerDNS01ChallengeSettings()
    )
    challenge_webhook: WebhookSettings = Field(
        None,
        description="Triggered after challenges are received from the upstream server but before they are answered. Requires a 20X status code returned or else the order will fail.",
    )


class ACMEFinalizerSettings(FinalizerSettings):
    type: SkipJsonSchema[Literal["acme"]] = "acme"
    module: SkipJsonSchema[str] = "certificat.modules.acme.backends.acme.ACMEFinalizer"

    @classmethod
    def get(cls) -> Self:
        settings = inject.instance(ApplicationSettings)
        if settings.finalizer.type == "acme":
            return settings.finalizer

    directory: HttpUrl = Field(
        description="Path to the ACME API endpoint. This usually ends with /directory."
    )
    account_kid: str = Field(
        None, description="External account binding key identifier."
    )
    account_hmac_key: str = Field(
        None, description="External account binding HMAC key."
    )
    account_email: str = Field(
        description="Email address used as a contact when binding an account."
    )
    skip_answering_challenges: bool = Field(
        False,
        description="Skip answering authorization challenges. This may be used if the upstream ACME server supports pre-authorization.",
    )

    finalization_timeout: int = Field(
        90,
        description="How long to poll the upstream server before finalization is canceled.",
    )
    client_user_agent: SkipJsonSchema[str] = Field(
        "certificat/acme-python", description="User agent of the ACME client."
    )

    challenges: SkipJsonSchema[ACMEFinalizerChallengeSettings] = Field(
        ACMEFinalizerChallengeSettings()
    )


class CERTINextExternalAccountBinding(BaseModel):
    directory: HttpUrl = Field(
        description="Path to the ACME API endpoint. This usually ends with /directory."
    )
    account_kid: str = Field("External account binding key identifier.")
    account_hmac_key: str = Field(
        None, description="External account binding HMAC key."
    )
    account_email: str = Field(
        description="Email address used when binding an account."
    )


class CERTINextACMEFinalizerSettings(FinalizerSettings):
    type: SkipJsonSchema[Literal["certinext-acme"]] = "certinext-acme"
    module: SkipJsonSchema[str] = (
        "certificat.modules.acme.backends.certinext_acme.CERTINextACMEFinalizer"
    )

    @classmethod
    def get(cls) -> Self:
        settings = inject.instance(ApplicationSettings)
        if settings.finalizer.type == "certinext-acme":
            return settings.finalizer

    single_domain_binding: CERTINextExternalAccountBinding = Field(
        description="ACME credentials used when creating a single-domain certificate."
    )
    multi_domain_binding: CERTINextExternalAccountBinding = Field(
        description="ACME credentials used when creating a multi-domain certificate."
    )

    skip_answering_challenges: bool = Field(
        False,
        description="Skip answering authorization challenges. This may be used if the upstream ACME server supports pre-authorization.",
    )

    finalization_timeout: int = Field(
        90,
        description="How long to poll the upstream server before finalization is canceled.",
    )
    client_user_agent: SkipJsonSchema[str] = Field(
        "certificat/acme-python", description="User agent of the ACME client."
    )


class CertiNextFinalizerSettings(FinalizerSettings):
    type: SkipJsonSchema[Literal["certinext"]] = "certinext"
    module: SkipJsonSchema[str] = (
        "certificat.modules.acme.backends.certinext.CertiNextFinalizer"
    )

    @classmethod
    def get(cls) -> Self:
        settings = inject.instance(ApplicationSettings)
        if settings.finalizer.type == "certinext":
            return settings.finalizer

    api_base: str = Field(
        "https://us-api.certinext.io/", description="Base URL of the CERTInext API."
    )
    org_number: str = Field(
        description="Organization ID that will be requesting the certificate."
    )
    product_variant: str = Field(
        "ov", description="Product variant, defaults to organization validated."
    )
    product_code: str = Field(description="Unique product code for the order.")
    oauth_client_id: str = Field(
        "Client ID for the OAuth client credentials grant request."
    )
    oauth_client_secret: str = Field(
        "Client secret for the OAuth client credentials grant request."
    )

    requestor_name: str = Field("CertifiCat", description="Name of the requestor.")
    requestor_email: str = Field(description="Email of the requestor.")
    requestor_phone: str = Field(description="Phone number of the requestor.")
    requestor_designation: str = Field(
        "+1", description="Designation of the requestor."
    )

    agreement_signer: str = Field(
        description="Name of the agreement signer for certificate issuance."
    )
    agreement_signer_place: str = Field(
        description="Place of the agreement signer for certificate issuance."
    )

    order_remarks: str = Field(
        "Submitted by CertifiCat",
        description="Optional order remarks to include with each certificate order.",
    )

    poll_deadline: int = Field(
        60 * 5,
        description="The finalizer task will continue to poll the CERTINext backend to check if the certificate is fulfilled until hitting this deadline in seconds.",
    )
    poll_interval: int = Field(
        1,
        description="The finalizer will sleep for this duration between polling certificate order status.",
    )


class SectigoFinalizerSettings(FinalizerSettings):
    model_config = SettingsConfigDict(
        validate_default=False, env_prefix="SECTIGO__", env_nested_delimiter="__"
    )

    type: SkipJsonSchema[Literal["sectigo"]] = "sectigo"
    module: SkipJsonSchema[str] = (
        "certificat.modules.acme.backends.sectigo.SectigoFinalizer"
    )

    @classmethod
    def get(cls) -> Self:
        settings = inject.instance(ApplicationSettings)
        if settings.finalizer.type == "sectigo":
            return settings.finalizer

    org_id: int = Field(description="Organization or department ID")
    cert_profile_id: int = Field(description="Certificate profile ID")
    cert_validity_period: int = Field(
        90,
        description="This must be set to one of the valid lifetimes for your certificate profile id.",
    )
    customer_uri: str = Field(
        description="Customer URI, found in the cert-manager URL.",
        examples=["`InCommon` `InCommon_test`"],
    )
    api_base: str = Field(
        "https://cert-manager.com/api/", description="Base URL of the cert-manager API."
    )
    api_user: str = Field(description="The API user performing the requests.")
    api_password: str = Field(description="The password for the API user.")
    approval_api_user: str = Field(
        description="If your API user is unable to approve requests you will need to provide a separate user."
    )
    approval_api_password: str = Field(
        description="The password for the approval API user."
    )
    external_requester_override: str | None = Field(
        None,
        description="This email address will receive all Sectigo certificate lifecycle emails instead of the registered account email.",
        required=False,
    )

    poll_deadline: int = Field(
        60 * 5,
        description="The finalizer task will continue to poll the Sectigo backend to check if the certificate is ready for approval or approved until hitting this deadline in seconds.",
    )


class LocalFinalizerSettings(FinalizerSettings):
    type: SkipJsonSchema[Literal["local"]] = "local"
    module: SkipJsonSchema[str] = (
        "certificat.modules.acme.backends.local.LocalFinalizer"
    )

    model_config = SettingsConfigDict(
        validate_default=False, env_prefix="LOCAL_CA__", env_nested_delimiter="__"
    )

    @classmethod
    def get(cls) -> Self:
        settings = inject.instance(ApplicationSettings)
        if settings.finalizer.type == "local":
            return settings.finalizer

    key: str = Field(
        description="PEM-formatted private key for the CA",
    )
    cert: str = Field(description="PEM-formatted public key for the CA")


type PolymorphicFinalizerSettings = (
    SkipJsonSchema[SectigoFinalizerSettings]
    | SkipJsonSchema[CertiNextFinalizerSettings]
    | LocalFinalizerSettings
    | ACMEFinalizerSettings
    | CERTINextACMEFinalizerSettings
)


class AlternativeFinalizerSettings(BaseModel):
    id: str = Field(
        description="Unique ID for this finalizer. This will be stored in the account and used to select the correct finalizer at certificate creation."
    )
    name: str = Field(
        description="A short descriptive name for the finalizer. This is presented in user interfaces when making selections."
    )
    description: str = Field(
        description="A short description of the finalizer. This is presented in user interfaces when making selections."
    )
    finalizer: PolymorphicFinalizerSettings = Field(
        discriminator="type",
        description="Which order finalizer module to use.",
        examples=[
            "`local` `acme` `certinext-acme`",
        ],
    )


class ApplicationSettings(Settings):
    model_config = SettingsConfigDict(
        validate_default=False,
        env_prefix="CERTIFICAT__",
        env_nested_delimiter="__",
    )

    DEFAULT_ACME_MOUNTPOINT: ClassVar[str] = "acme/"

    @classmethod
    def get(cls, force_reload=False) -> Self:
        return ConfigFile.load(force_reload=force_reload).certificat

    def get_deprecations(self):
        deprecations = []
        models: list[tuple[Settings, type[Settings], str]] = [
            (self, ApplicationSettings, "certificat")
        ]

        while models:
            curr_model, model_type, prefix = models.pop(0)
            for field_name, field in model_type.model_fields.items():
                concrete_field = getattr(curr_model, field_name)

                if issubclass(type(concrete_field), BaseModel):
                    models.append(
                        (
                            concrete_field,
                            concrete_field.__class__,
                            f"{prefix}.{field_name}",
                        )
                    )

                if field.deprecated and field_name in curr_model.model_fields_set:
                    deprecations.append(f"{prefix}.{field_name}: {field.deprecated}")

        return deprecations

    debug: bool | None = Field(
        False,
        description="Debug mode for the application. This should never be True for production.",
        deprecated="This field will be removed in a future version and is currently ignored.",
    )
    proto: Literal["http", "https"] | None = Field(
        "https",
        deprecated="This field is unused and will be removed in a future version, protocol is now determined at runtime.",
    )
    secret_key: str = Field(
        description=textwrap.dedent("""
            [Django SECRET_KEY.](https://docs.djangoproject.com/en/6.1/ref/settings/#std-setting-SECRET_KEY) This should be set to a unique, unpredictable value.
            
            You can generate a secret key by using the following snippet: 
            
            ``` bash
            tr -dc 'a-zA-Z0-9!@#$%^&*(-_=+)' < /dev/urandom | head -c 50; echo
            ```
        """)
    )
    session_cookie_age: int = Field(
        60 * 60 * 8,
        description="Django SESSION_COOKIE_AGE. This is the maximum age of the session cookie in seconds.",
    )
    time_zone: str = Field(
        "America/New_York",
        description="Django TIME_ZONE, used mostly for date localization.",
    )
    url_root: str = Field(
        description=textwrap.dedent("""
            The url root is used to generate absolute urls to the application. It should not contain path and parameters.
            !!! warning
                If your url_root changes your existing ACME accounts will become unusable. This is due to [request URL integrity](https://datatracker.ietf.org/doc/html/rfc8555#section-6.4).
        """),
        examples=["`https://acme.edu/`"],
    )
    web_ui_mountpoint: BetaFeature[str] = Field(
        "", description="The root of the web UI."
    )
    web_api_mountpoint: BetaFeature[str] = Field(
        "api/", description="The root of the web API."
    )
    web_acme_mountpoint: BetaFeature[str] = Field(
        DEFAULT_ACME_MOUNTPOINT, description="The root of the ACME server."
    )
    staticfiles_root: SkipJsonSchema[str | None] = Field(
        None,
        description="Location of static files. This usually doesn't have to be changed.",
        required=False,
    )
    root_urlconf: SkipJsonSchema[str | None] = Field(
        None,
        description="Dotted path to the root urlconfig. This usually doesn't have to be changed.",
        required=False,
    )

    logging: LoggingSettings = Field(
        LoggingSettings(), description="Logging levels for CertifiCat components"
    )
    db: (
        MariaDBDatabaseSettings
        | PostgresDatabaseSettings
        | SkipJsonSchema[SQLiteDatabaseSettings]
    ) = Field(
        discriminator="type",
        description="Database connection settings. CertifiCat requires an external database to store ACME and management state.",
    )
    redis: RedisSettings = Field(
        description="Redis connection settings. CertifiCat requires Redis to store cache and faciliate background jobs."
    )
    cache: SkipJsonSchema[RedisCacheSettings | LocalMemoryCacheSettings] = Field(
        RedisCacheSettings(),
        discriminator="type",
        exclude=True,  # This isn't exposed in documentation for the user
    )
    task_queue: TaskQueueSettings = Field(
        TaskQueueSettings(),
        description="Settings for the Redis-powered Huey task queue.",
    )
    theming: ThemeSettings = Field(
        ThemeSettings(),
        description="Theming and customization settings for the web front-end.",
    )

    trust_proxy_forwarded_proto: bool | None = Field(
        False,
        description="Signals to the app to trust the HTTP_X_FORWARDED_PROTO header if True.",
        deprecated="This field is ignored and will be removed in the future. The url_root option is used to build and validate URLs.",
    )
    authentication: (
        SAMLAuthSettings | SkipJsonSchema[LocalAuthSettings] | RemoteAuthSettings
    ) = Field(
        discriminator="type",
        description="Authentication settings for the web frontend. This controls how you authenticate and automatically provision access to the CertifiCat HTML service.",
    )

    hmac_id_length: int = Field(
        40,
        description="The length of the hmac id generated for an ACME external account binding.",
    )
    hmac_key_length: int = Field(
        90,
        description="The length of the hmac key generated for an ACME external account binding.",
    )

    challenge_retry_delay: int = Field(
        2, description="How long to wait between challenge retries in seconds."
    )
    challenge_max_retries: int = Field(
        5,
        description="How many challenge retries to perform before marking the challenge invalid.",
    )
    finalize_retry_delay: int = Field(
        10,
        description="How long to wait between order finalization retries in seconds.",
    )
    finalize_max_retries: int = Field(
        10,
        description="How many order finalization retries to perform before marking the order invalid.",
    )

    finalizer: PolymorphicFinalizerSettings = Field(
        discriminator="type",
        description="Which order finalizer module to use. The server is designed to finalize all requests against one default backend. This will be the backend initially used by all accounts.",
    )

    alternative_finalizers: list[AlternativeFinalizerSettings] = Field(
        [],
        description="A list of alternative finalizers that can be used to request certificates through manual configuration.",
        examples=[
            textwrap.dedent("""
            ``` yaml
            certificat: 
              alternative_finalizers:
                - id: "alt-finalizer-1"
                  name: "Alternative Finalizer 1"
                  description: "A description for the web UI"
                  finalizer: ... certificat.finalizer ...

                - id: "alt-finalizer-2"
                  name: "Alternative Finalizer 2"
                  description: "A different description for the web UI"
                  finalizer: ... certificat.finalizer ...
            ```
            """)
        ],
    )

    delete_invalid_orders: bool = Field(
        True,
        description="Purge invalid orders after some amount of time.",
    )
    beacon_enabled: bool = Field(
        True,
        description="Send tracking information about platform usage to RIT.",
    )
    show_version: bool = Field(False, description="Show the version on the website.")

    healthcheck_allowed_networks: list[str] = Field(
        ["127.0.0.1/32"], description="Networks allowed to access the health endpoints."
    )
    huey_health_file: SkipJsonSchema[str] = Field("/tmp/huey-ping")

    @field_validator("web_ui_mountpoint", "web_api_mountpoint", "web_acme_mountpoint")
    @classmethod
    def validate_mountpoint(cls, value: str) -> str:
        final_value = value.strip("/") + "/"
        pattern = r"[a-zA-Z0-9/\-_]*"

        if final_value == cls.DEFAULT_ACME_MOUNTPOINT:
            raise ValueError(
                f"'{value}' cannot be used as a custom mountpoint. If you're trying to configure acme, consider '/acmev2/'"
            )

        if not re.fullmatch(pattern, final_value):
            raise ValueError(
                "mountpoint may only contain letters, numbers, forward slashes, hyphens, and underscores."
            )

        if final_value.strip() == "/":
            final_value = ""

        return final_value


class LocalACMESettings(ACMESettings):
    @classmethod
    def get(cls, force_reload=False) -> Self:
        return ConfigFile.load(force_reload=force_reload).acme


class ConfigFile(BaseSettings):
    model_config = SettingsConfigDict(validate_default=False, from_attributes=True)

    certificat: ApplicationSettings
    acme: LocalACMESettings = Field(default=ACMESettings(eab_required=True))

    @classmethod
    def load(cls, force_reload=False) -> Self:
        _config = getattr(cls, "_config", None)
        if force_reload:
            _config = None

        if not _config:
            config_file = os.environ.get("CERTIFICAT__CONFIG")
            if not config_file:
                print(
                    "CERTIFICAT__CONFIG environment variable should contain a config path, instead was empty."
                )
                exit(1)

            if not os.path.exists(config_file):
                print("Could not load config at path: " + config_file)
                exit(1)

            with open(config_file) as file:
                config_values = yaml.safe_load(file)

            try:
                _config = ConfigFile.model_validate(config_values, from_attributes=True)
                cls._config = _config
            except ValidationError as err:
                print("Fatal error loading config at " + config_file)
                for err in err.errors():
                    str_loc = [str(p) for p in err.get("loc")]
                    print(f"  {'.'.join(str_loc)}: {err.get('msg')}")

                exit(1)
            except Exception as err:
                print("Fatal error loading config at " + config_file)
                print("  " + str(err))

                exit(1)

        return _config

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """
        Define the sources and their order for loading the settings values.

        Args:
            settings_cls: The Settings class.
            init_settings: The `InitSettingsSource` instance.
            env_settings: The `EnvSettingsSource` instance.
            dotenv_settings: The `DotEnvSettingsSource` instance.
            file_secret_settings: The `SecretsSettingsSource` instance.

        Returns:
            A tuple containing the sources and their order for loading the settings values.
        """

        return (init_settings,)
