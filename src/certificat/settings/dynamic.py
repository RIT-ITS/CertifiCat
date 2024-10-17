from pydantic_settings import BaseSettings, SettingsConfigDict
from acmev2.settings import ACMESettings


class DatabaseSettings(BaseSettings):
    engine: str = "django.db.backends.mysql"
    name: str
    user: str
    password: str
    host: str
    port: int = 3306


class RedisSettings(BaseSettings):
    host: str
    password: str
    port: int = 6379


class LocalCASettings(BaseSettings):
    model_config = SettingsConfigDict(validate_default=False, env_prefix="LOCAL_CA_")

    key: str
    cert: str


class SectigoSettings(BaseSettings):
    model_config = SettingsConfigDict(validate_default=False, env_prefix="SECTIGO_")

    org_id: int
    cert_profile_id: int
    customer_uri: str
    api_base: str
    api_user: str
    api_password: str
    approval_api_user: str
    approval_api_password: str
    external_requester_override: str
    cert_validity_period: int = 90

    poll_deadline: int = 60 * 5


class ApplicationSettings(BaseSettings):
    model_config = SettingsConfigDict(
        validate_default=False, env_prefix="CERTIFICAT_", env_nested_delimiter="_"
    )

    debug: bool = False
    secret_key: str
    time_zone: str = "UTC"
    url_root: str

    db: DatabaseSettings
    redis: RedisSettings

    challenge_retry_delay: int = 2
    challenge_max_retries: int = 5
    finalize_retry_delay: int = 10
    finalize_max_retries: int = 10

    ca_module: str = "certificat.modules.acme.backends.sectigo.SectigoBackend"


app_settings = ApplicationSettings()
acme_settings = ACMESettings()
