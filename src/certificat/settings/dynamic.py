from typing import List, Literal, Mapping
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    external_requester_override: str | None
    cert_validity_period: int = 90

    poll_deadline: int = 60 * 5


class SAMLSettings(BaseSettings):
    model_config = SettingsConfigDict(validate_default=False, env_prefix="SAML_")

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


class ApplicationSettings(BaseSettings):
    model_config = SettingsConfigDict(
        validate_default=False, env_prefix="CERTIFICAT_", env_nested_delimiter="_"
    )

    debug: bool = False
    secret_key: str
    time_zone: str = "America/New_York"
    url_root: str

    db: DatabaseSettings
    redis: RedisSettings

    login_method: Literal["local", "saml"] = "saml"

    hmac_id_length: int = 40
    hmac_key_length: int = 90

    challenge_retry_delay: int = 2
    challenge_max_retries: int = 5
    finalize_retry_delay: int = 10
    finalize_max_retries: int = 10

    finalizer_module: str = "certificat.modules.acme.backends.local.LocalFinalizer"
    delete_invalid_orders: bool = True
