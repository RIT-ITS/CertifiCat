from typing import List, Literal, Mapping, Self, Optional, Union

from pydantic import Field, ValidationError, BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)
import os
import yaml
from acmev2.settings import ACMESettings
import multiprocessing
import inject


class Settings(BaseSettings):
    pass


class DatabaseSettings(BaseModel):
    type: Literal["none"]

    def to_backend(self):
        raise Exception("Databaser settings were not configured.")


class MariaDBDatabaseSettings(BaseModel):
    type: Literal["mysql"]
    engine: str = "django.db.backends.mysql"
    name: str = Field(
        description="The database to use after a connection is established."
    )
    user: str = Field(description="User for the database connection.")
    password: str = Field(None, description="Password for the database connection")
    host: str = Field(None, description="Host for the database connection")
    port: int = 3306
    options: dict = Field({}, description="Options passed to the driver")
    table_prefix: str = Field(
        "", description="An optional table prefix for every table in the database."
    )

    def to_backend(self):
        return {
            "ENGINE": self.engine,
            "NAME": self.name,
            "USER": self.user,
            "PASSWORD": self.password,
            "HOST": self.host,
            "PORT": self.port,
            "OPTIONS": self.options,
        }


class PostgresDatabaseSettings(BaseModel):
    type: Literal["postgresql"]
    engine: str = "django.db.backends.postgresql"
    name: str = Field(
        description="The database to use after a connection is established."
    )
    user: str = Field(description="User for the database connection.")
    password: str = Field(None, description="Password for the database connection")
    host: str = Field(None, description="Host for the database connection")
    port: int = 5432
    options: dict = Field({}, description="Options passed to the driver")
    table_prefix: str = Field(
        "", description="An optional table prefix for every table in the database."
    )

    def to_backend(self):
        return {
            "ENGINE": self.engine,
            "NAME": self.name,
            "USER": self.user,
            "PASSWORD": self.password,
            "HOST": self.host,
            "PORT": self.port,
            "OPTIONS": self.options,
        }


class SQLiteDatabaseSettings(BaseModel):
    type: Literal["sqlite"]
    engine: str = "django.db.backends.sqlite3"
    name: str = Field(description="The location of the sqlite database.")
    options: dict = Field({}, description="Options passed to the driver")

    def to_backend(self):
        return {
            "ENGINE": self.engine,
            "NAME": self.name,
            "OPTIONS": self.options,
        }


class TaskQueueSettings(BaseModel):
    workers: int = Field(
        max(25, min(multiprocessing.cpu_count() * 25, 100)),
        description="Number of workers in the Huey task queue.",
    )


class CacheSettings(BaseModel):
    type: Literal["django.core.cache.backends.None"]

    def to_backend(self):
        raise Exception("Cache settings were not configured.")


class RedisCacheSettings(CacheSettings):
    type: Literal["redis"] = "redis"
    backend: str = "django.core.cache.backends.redis.RedisCache"

    def to_backend(self):
        redis_settings = inject.instance(ApplicationSettings).redis
        return {
            "BACKEND": self.backend,
            "LOCATION": f"redis://:{redis_settings.password}@{redis_settings.host}:{redis_settings.port}",
            "OPTIONS": {"health_check_interval": 30},
        }


class LocalMemoryCacheSettings(CacheSettings):
    type: Literal["local"]
    backend: str = "django.core.cache.backends.locmem.LocMemCache"

    def to_backend(self):
        return {"BACKEND": self.backend}


class RedisSettings(BaseModel):
    backend: Literal["django.core.cache.backends.redis.RedisCache"] = (
        "django.core.cache.backends.redis.RedisCache"
    )
    host: str = Field(description="Host for the redis connection.")
    password: str = Field(description="Password for the Redis connection")
    port: int = 6379


class LoggingSettings(BaseModel):
    certificat_level: str | None = "INFO"
    huey_level: str | None = "INFO"
    django_level: str | None = "INFO"
    acmev2_level: str | None = "INFO"


class ThemeSettings(BaseModel):
    global_css: str | None = None


class SAMLSPSettings(BaseModel):
    entity_id: str = Field(
        description="SAML service entity id. It should be unique and a URI."
    )
    name: str = Field("CertifiCat", description="The SP name")
    key_file: str = Field(
        description="The location of the PEM-formatted private key file"
    )
    cert_file: str = Field(
        description="The location of the PEM-formatted public key file"
    )
    signing_algorthm: str = Field(
        "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
        description="The default signing algorithm.",
    )
    digest_algorithm: str = Field(
        "http://www.w3.org/2001/04/xmlenc#sha256",
        description="The default digest algorithm",
    )
    force_authn: bool = Field(False, description="Disable SSO session reuse on login")
    allow_unsolicited: bool = Field(True, description="Allow IdP-initiated SSO.")


class RemoteIdP(BaseModel):
    url: str = Field(description="IdP metadata URL.")
    cert: Optional[str] = Field(
        None, required=False, description="Signing certificate for the remote metadata."
    )


class MDQ(BaseModel):
    url: str = Field(description="Metadata query URL.")
    cert: Optional[str] = Field(
        None,
        required=False,
        description="Signing certificate for the metadata query URL.",
    )
    freshness_period: str = "P0Y0M0DT2H0M0S"


class SAMLIdPSettings(BaseModel):
    local: List[str] = Field([], description="A list of local metadata files.")
    remote: List[RemoteIdP] = Field(
        [], description="A list of remote metadata providers.", required=False
    )
    mdq: List[MDQ] = Field(
        [], description="A list of metadata query providers.", required=False
    )


class SAMLDiscoverySettings(BaseModel):
    service: str = Field(
        description="SAML discovery service. This feature is experimental and subject to change."
    )
    response: List[str] = Field(
        [],
        description="Discovery response endpoints. This feature is experimental and subject to change.",
    )


class LocalAuthAdminSettings(BaseModel):
    username: str
    password: str
    email: str


class LocalAuthSettings(BaseModel):
    type: Literal["local"]
    admin: LocalAuthAdminSettings


class RemoteAuthSettings(BaseModel):
    type: Literal["remote"] = "remote"
    user_header: str = "HTTP_USER"
    administrators: List[str] = Field(
        [],
        description="A list of user principals who will automatically be given administrator privileges on login.",
    )
    force_logout_if_no_header: bool = True
    log_http_headers: bool = False
    attribute_mapping: Mapping[str, List[str]] = Field(
        {
            "HTTP_USER_EMAIL": "email",
            "HTTP_USER_FIRSTNAME": "first_name",
            "HTTP_USER_LASTNAME": "last_name",
        },
        description="A dictionary mapping of src:target where attributes are mapped from headers to Django attributes.",
    )
    redirect_template: str = Field(
        description="Templated URL target for redirects. The redirect variable is substituted with the URL encoded path of the protected resource.",
        examples=["https://auth.example/?redirect_to={ redirect }"],
    )


class SAMLAuthSettings(BaseModel):
    type: Literal["saml"] = "saml"
    model_config = SettingsConfigDict(
        validate_default=False,
        env_prefix="SAML__",
        from_attributes=True,
        env_nested_delimiter="__",
    )

    @classmethod
    def get(cls, force_reload=False) -> Self:
        return ConfigFile.load(force_reload=force_reload).saml

    debug: bool = Field(
        False, description="The debug setting for the Django SAML plugin."
    )
    xmlsec_binary: str = Field(
        "/usr/bin/xmlsec1", description="The absolute path to the xmlsec binary."
    )
    session_cookie: str = Field(
        "snickerdoodle", description="The name of the session cookie."
    )
    administrators: List[str] = Field(
        [],
        description="A list of user principals who will automatically be given administrator privileges on login.",
    )

    group_attribute: str = Field(
        "memberof",
        description="The name (or translated name) of the group attribute in the returned SAML assertion",
    )
    group_sync_prefix: str = Field(
        "SAML/",
        description="New groups synced from SAML will be prefixed with this identifier.",
    )

    sp: SAMLSPSettings
    idp: SAMLIdPSettings
    discovery: SAMLDiscoverySettings | None = None

    attribute_mapping: Mapping[str, List[str]] = Field(
        {
            "uid": ["username"],
            "eduPersonPrincipalName": ["username"],
            "eduPersonTargetedID": ["username"],
            "mail": ["email"],
            "givenName": ["first_name"],
            "sn": ["last_name"],
        },
        description="A dictionary mapping of src:[target] where attributes are mapped from SAML responses to Django attributes. This is designed to work with a yaml config, not environment variables.",
    )


class FinalizerSettings(BaseModel):
    type: Literal["none"]
    module: str


class EMSignFinalizerSettings(FinalizerSettings):
    model_config = SettingsConfigDict(
        validate_default=False, env_prefix="EMSIGN__", env_nested_delimiter="__"
    )

    type: Literal["emsign"] = "emsign"
    module: str = "certificat.modules.acme.backends.emsign.EMSignFinalizer"

    @classmethod
    def get(cls) -> Self:
        settings = inject.instance(ApplicationSettings)
        if settings.finalizer.type == "emsign":
            return settings.finalizer

    api_base: str = Field(
        "https://localhost/api/", description="Base URL of the emSign API"
    )
    account_number: str = Field(description="Account number (Org. ID)")
    auth_key: str = Field(description="Authorization key for API access")
    product_code: str = Field(description="Unique product code for the order")

    prevetted_org_number: str = Field(
        description="Pre-vetted organization id to pair with the pre-vetting token"
    )
    prevetting_token: str = Field(
        description="Pre-vetting token for automatically submitting an order"
    )

    requestor_name: str = Field("CertifiCat", description="Name of the requestor")
    requestor_isd_code: str = Field("+1", description="ISD code of the requestor")
    requestor_mobile_number: str = Field(description="Mobile number of the requestor")
    requestor_email: str = Field(description="Email of the requestor")

    poll_deadline: int = Field(
        60 * 5,
        description="The finalizer task will continue to poll the EMSign backend to check if the certificate is fulfilled until hitting this deadline in seconds.",
    )
    poll_interval: int = 1


class SectigoFinalizerSettings(FinalizerSettings):
    model_config = SettingsConfigDict(
        validate_default=False, env_prefix="SECTIGO__", env_nested_delimiter="__"
    )

    type: Literal["sectigo"]
    module: str = "certificat.modules.acme.backends.sectigo.SectigoFinalizer"

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
        examples=["InCommon", "InCommon_test"],
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
    external_requester_override: Optional[str] = Field(
        None,
        description="This email address will receive all Sectigo certificate lifecycle emails instead of the registered account email.",
        required=False,
    )

    poll_deadline: int = Field(
        60 * 5,
        description="The finalizer task will continue to poll the Sectigo backend to check if the certificate is ready for approval or approved until hitting this deadline in seconds.",
    )


class LocalFinalizerSettings(FinalizerSettings):
    type: Literal["local"]
    module: str = "certificat.modules.acme.backends.local.LocalFinalizer"

    model_config = SettingsConfigDict(
        validate_default=False, env_prefix="LOCAL_CA__", env_nested_delimiter="__"
    )

    @classmethod
    def get(cls) -> Self:
        settings = inject.instance(ApplicationSettings)
        if settings.finalizer.type == "local":
            return settings.finalizer

    key: str = Field(description="PEM-formatted private key for the CA")
    cert: str = Field(description="PEM-formatted public key for the CA")


class ApplicationSettings(Settings):
    model_config = SettingsConfigDict(
        validate_default=False, env_prefix="CERTIFICAT__", env_nested_delimiter="__"
    )

    @classmethod
    def get(cls, force_reload=False) -> Self:
        return ConfigFile.load(force_reload=force_reload).certificat

    debug: Optional[bool] = Field(
        False,
        description="Debug mode for the application. This should never be True for production.",
    )
    proto: Optional[Literal["http", "https"]] = Field("https")
    secret_key: str = Field(
        description="Django SECRET_KEY. This should be set to a unique, unpredictable value."
    )
    time_zone: str = "America/New_York"
    url_root: str = Field(
        description="The url root is used to generate absolute urls to the application.",
        examples=["https://acme.edu"],
    )
    staticfiles_root: Optional[str] = Field(
        None,
        description="Location of static files. This usually doesn't have to be changed.",
        required=False,
    )
    root_urlconf: Optional[str] = Field(
        None,
        description="Dotted path to the root urlconfig. This usually doesn't have to be changed.",
        required=False,
    )

    logging: LoggingSettings = LoggingSettings()
    db: Union[
        MariaDBDatabaseSettings, PostgresDatabaseSettings, SQLiteDatabaseSettings
    ] = Field(discriminator="type")
    redis: RedisSettings
    cache: Optional[Union[RedisCacheSettings, LocalMemoryCacheSettings]] = Field(
        RedisCacheSettings(), discriminator="type"
    )
    task_queue: TaskQueueSettings = TaskQueueSettings()
    theming: ThemeSettings = ThemeSettings()

    trust_proxy_forwarded_proto: Optional[bool] = Field(
        False,
        description="Signals to the app to trust the HTTP_X_FORWARDED_PROTO header if True.",
    )
    authentication: Union[SAMLAuthSettings, LocalAuthSettings, RemoteAuthSettings] = (
        Field(discriminator="type")
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

    finalizer: Union[
        SectigoFinalizerSettings, EMSignFinalizerSettings, LocalFinalizerSettings
    ] = Field(
        discriminator="type",
        description="Which order finalizer module to use. The server is designed to finalize all requests against one backend.",
        examples=[
            "local",
            "sectigo",
            "emsign",
        ],
    )
    delete_invalid_orders: bool = Field(
        True,
        description="If set to True, invalid orders will be purged after some time.",
    )
    beacon_enabled: bool = Field(
        True,
        description="If true, will send tracking information about usage to RIT. All tracking info is logged.",
    )
    show_version: bool = Field(False, description="Show the version on the website.")

    healthcheck_allowed_networks: List[str] = Field(
        ["127.0.0.1/32"], description="Networks allowed to access the health endpoints."
    )
    huey_health_file: str = Field("/tmp/huey-ping")


class LocalACMESettings(ACMESettings):
    @classmethod
    def get(cls, force_reload=False) -> Self:
        return ConfigFile.load(force_reload=force_reload).acme


class ConfigFile(BaseSettings):
    model_config = SettingsConfigDict(validate_default=False, from_attributes=True)

    certificat: ApplicationSettings
    acme: LocalACMESettings = Field(default=ACMESettings())

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
                setattr(cls, "_config", _config)
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
