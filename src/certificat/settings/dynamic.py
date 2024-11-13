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


class Settings(BaseSettings):
    pass


class DatabaseSettings(Settings):
    engine: str = "django.db.backends.mysql"
    name: str
    user: str
    password: str
    host: str
    port: int = 3306


class RedisSettings(Settings):
    host: str
    password: str
    port: int = 6379


class ApplicationSettings(Settings):
    model_config = SettingsConfigDict(
        validate_default=False, env_prefix="CERTIFICAT_", env_nested_delimiter="_"
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
    redis: RedisSettings

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
    model_config = SettingsConfigDict(validate_default=False, env_prefix="LOCAL_CA_")

    @classmethod
    def get(cls, force_reload=False) -> Self:
        return ConfigFile.load(force_reload=force_reload).local_finalizer

    key: str
    cert: str


class SectigoSettings(Settings):
    model_config = SettingsConfigDict(validate_default=False, env_prefix="SECTIGO_")

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


class SAMLSettings(Settings):
    model_config = SettingsConfigDict(
        validate_default=False, env_prefix="SAML_", from_attributes=True
    )

    @classmethod
    def get(cls, force_reload=False) -> Self:
        return ConfigFile.load(force_reload=force_reload).saml

    debug: bool = False
    xmlsec_binary: str = "/usr/bin/xmlsec1"
    session_cookie: str = "snickerdoodle"
    administrators: List[str] = []
    entity_id: str
    attribute_mapping: Mapping[str, str] = {
        "uid": "username",
        "mail": "email",
        "givenName": "first_name",
        "sn": "last_name",
    }
    group_attribute: str = "memberof"
    group_prefix: str = "<SAML>"
    service_name: str = "CertifiCat"
    signing_algorthm: str = "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"
    digest_algorithm: str = "http://www.w3.org/2001/04/xmlenc#sha256"
    force_authn: bool = False

    idp_metadata_path: str
    key_path: str
    cert_path: str


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
            config_file = os.environ.get("CERTIFICAT_CONFIG")
            if not config_file:
                print(
                    "CERTIFICAT_CONFIG environment variable should contain a config path, instead was empty."
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
