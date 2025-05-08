from typing import List, Literal, Mapping, Self, Optional

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


class Settings(BaseSettings):
    pass


class DatabaseSettings(BaseModel):
    engine: str = "django.db.backends.mysql"
    name: str = Field(
        description="The database to use after a connection is established."
    )
    user: str = Field(description="User for the database connection.")
    password: str = Field(description="Password for the database connection")
    host: str = Field(description="Host for the database connection")
    port: int = 3306
    table_prefix: str = Field(
        "", description="An optional table prefix for every table in the database."
    )


class TaskQueueSettings(BaseModel):
    workers: int = Field(
        max(25, min(multiprocessing.cpu_count() * 25, 100)),
        description="Number of workers in the Huey task queue.",
    )


class RedisSettings(BaseModel):
    host: str = Field(description="Host for the redis connection.")
    password: str = Field(description="Password for the Redis connection")
    port: int = 6379


class LoggingSettings(BaseModel):
    certificat_level: str | None = "INFO"
    huey_level: str | None = "INFO"
    django_level: str | None = "INFO"
    acmev2_level: str | None = "INFO"


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
    staticfiles_root: Optional[str] = Field(None, description="Location of static files. This usually doesn't have to be changed.", required=False)
    logging: LoggingSettings = LoggingSettings()
    db: DatabaseSettings
    redis: RedisSettings
    task_queue: TaskQueueSettings = TaskQueueSettings()

    trust_proxy_forwarded_proto: Optional[bool] = Field(
        False,
        description="Signals to the app to trust the HTTP_X_FORWARDED_PROTO header if True.",
    )
    login_method: Literal["local", "saml"] = Field(
        "saml",
        description="Default login method for the app. This defaults to saml, the app has minimal support for local outside of debugging.",
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

    finalizer_module: str = Field(
        "certificat.modules.acme.backends.local.LocalFinalizer",
        description="Which order finalizer module to use. The server is designed to finalize all requests against one backend.",
        examples=[
            "certificat.modules.acme.backends.local.LocalFinalizer",
            "certificat.modules.acme.backends.sectigo.SectigoFinalizer",
        ],
    )
    delete_invalid_orders: bool = Field(
        True,
        description="If set to True, invalid orders will be purged after some time.",
    )


class LocalCASettings(BaseModel):
    model_config = SettingsConfigDict(
        validate_default=False, env_prefix="LOCAL_CA__", env_nested_delimiter="__"
    )

    @classmethod
    def get(cls, force_reload=False) -> Self:
        return ConfigFile.load(force_reload=force_reload).local_finalizer

    key: str = Field(description="PEM-formatted private key for the CA")
    cert: str = Field(description="PEM-formatted public key for the CA")


class SectigoSettings(BaseModel):
    model_config = SettingsConfigDict(
        validate_default=False, env_prefix="SECTIGO__", env_nested_delimiter="__"
    )

    @classmethod
    def get(cls) -> Self:
        return ConfigFile.load().sectigo_finalizer

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


class SAMLSettings(BaseModel):
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


class LocalACMESettings(ACMESettings):
    @classmethod
    def get(cls, force_reload=False) -> Self:
        return ConfigFile.load(force_reload=force_reload).acme


class ConfigFile(BaseSettings):
    model_config = SettingsConfigDict(validate_default=False, from_attributes=True)

    certificat: ApplicationSettings
    acme: LocalACMESettings = Field(default=ACMESettings())
    saml: Optional[SAMLSettings] = None
    sectigo_finalizer: Optional[SectigoSettings] = None
    local_finalizer: Optional[LocalCASettings] = None

    @classmethod
    def load(cls, force_reload=False):
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

                match _config.certificat.login_method:
                    case "saml":
                        if _config.saml is None:
                            raise Exception(
                                "Config file must contain 'saml' section if 'saml' auth is requested"
                            )

                match _config.certificat.finalizer_module:
                    case "certificat.modules.acme.backends.local.LocalFinalizer":
                        if _config.local_finalizer is None:
                            raise Exception(
                                "Config file must contain 'local_finalizer' section if 'LocalFinalizer' backend is requested"
                            )
                    case "certificat.modules.acme.backends.sectigo.SectigoFinalizer":
                        if _config.sectigo_finalizer is None:
                            raise Exception(
                                "Config file must contain 'sectigo_finalizer' section if 'SectigoFinalizer' backend is requested"
                            )

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
