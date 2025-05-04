from typing import Any, List, Literal, Mapping, Self
from pydantic import Field, ValidationError
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


class DatabaseSettings(Settings):
    engine: str = "django.db.backends.mysql"
    name: str
    user: str
    password: str
    host: str
    port: int = 3306
    table_prefix: str = ""


class TaskQueueSettings(Settings):
    workers: int = max(25, min(multiprocessing.cpu_count() * 25, 100))


class RedisSettings(Settings):
    host: str
    password: str
    port: int = 6379


class LoggingSettings(Settings):
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

    debug: bool = False
    secret_key: str
    time_zone: str = "America/New_York"
    url_root: str
    staticfiles_root: str | None = None

    db: DatabaseSettings
    task_queue: TaskQueueSettings | None = TaskQueueSettings()
    redis: RedisSettings
    logging: LoggingSettings | None = LoggingSettings()

    trust_proxy_forwarded_proto: bool = False
    login_method: Literal["local", "saml"] = "saml"

    hmac_id_length: int = 40
    hmac_key_length: int = 90

    challenge_retry_delay: int = 2
    challenge_max_retries: int = 5
    finalize_retry_delay: int = 10
    finalize_max_retries: int = 10

    finalizer_module: (
        Literal[
            "certificat.modules.acme.backends.local.LocalFinalizer",
            "certificat.modules.acme.backends.sectigo.SectigoFinalizer",
        ]
        | Any
    ) = "certificat.modules.acme.backends.local.LocalFinalizer"
    delete_invalid_orders: bool = True


class LocalCASettings(Settings):
    model_config = SettingsConfigDict(
        validate_default=False, env_prefix="LOCAL_CA__", env_nested_delimiter="__"
    )

    @classmethod
    def get(cls, force_reload=False) -> Self:
        return ConfigFile.load(force_reload=force_reload).local_finalizer

    key: str
    cert: str


class SectigoSettings(Settings):
    model_config = SettingsConfigDict(
        validate_default=False, env_prefix="SECTIGO__", env_nested_delimiter="__"
    )

    @classmethod
    def get(cls) -> Self:
        return ConfigFile.load().sectigo_finalizer

    org_id: int
    cert_profile_id: int
    customer_uri: str
    api_base: str
    api_user: str
    api_password: str
    approval_api_user: str
    approval_api_password: str
    external_requester_override: str | None
    cert_validity_period: int = 90

    poll_deadline: int = 60 * 5


class SAMLSPSettings(Settings):
    entity_id: str
    name: str = "CertifiCat"
    key_file: str
    cert_file: str
    signing_algorthm: str = "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"
    digest_algorithm: str = "http://www.w3.org/2001/04/xmlenc#sha256"
    force_authn: bool = False
    allow_unsolicited: bool = True


class RemoteIdP(Settings):
    url: str
    cert: str | None = None


class MDQ(Settings):
    url: str
    cert: str | None = None
    freshness_period: str = "P0Y0M0DT2H0M0S"


class SAMLIdPSettings(Settings):
    local: List[str] = []
    remote: List[RemoteIdP] = []
    mdq: List[MDQ] = []


class SAMLDiscoverySettings(Settings):
    service: str
    response: List[str] = []


class SAMLSettings(Settings):
    model_config = SettingsConfigDict(
        validate_default=False,
        env_prefix="SAML__",
        from_attributes=True,
        env_nested_delimiter="__",
    )

    @classmethod
    def get(cls, force_reload=False) -> Self:
        return ConfigFile.load(force_reload=force_reload).saml

    debug: bool = False
    xmlsec_binary: str = "/usr/bin/xmlsec1"
    session_cookie: str = "snickerdoodle"
    administrators: List[str] = []

    group_attribute: str = "memberof"
    group_sync_prefix: str = "SAML/"

    sp: SAMLSPSettings
    idp: SAMLIdPSettings
    discovery: SAMLDiscoverySettings | None = None

    attribute_mapping: Mapping[str, List[str]] = {
        "uid": ["username"],
        "eduPersonPrincipalName": ["username"],
        "eduPersonTargetedID": ["username"],
        "mail": ["email"],
        "givenName": ["first_name"],
        "sn": ["last_name"],
    }


class LocalACMESettings(ACMESettings):
    @classmethod
    def get(cls, force_reload=False) -> Self:
        return ConfigFile.load(force_reload=force_reload).acme


class ConfigFile(BaseSettings):
    model_config = SettingsConfigDict(validate_default=False, from_attributes=True)

    certificat: ApplicationSettings
    acme: LocalACMESettings = Field(default=ACMESettings())
    saml: SAMLSettings | None = None
    sectigo_finalizer: SectigoSettings | None = None
    local_finalizer: LocalCASettings | None = None

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
                    print(f"  {'.'.join(err.get('loc'))}: {err.get('msg')}")

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
