"""Resolves which configured finalizer an account uses and fingerprints finalizer
settings so changes to them can be tracked."""

import hashlib
import hmac
import json
from dataclasses import dataclass

from django.conf import settings

from certificat.settings.dynamic import (
    ApplicationSettings,
    PolymorphicFinalizerSettings,
)

DEFAULT_FINALIZER_SHORT_NAME = "default"


@dataclass(frozen=True)
class ConfiguredFinalizer:
    short_name: str
    name: str
    description: str
    settings: PolymorphicFinalizerSettings


def _default_finalizer(app_settings: ApplicationSettings) -> ConfiguredFinalizer:
    return ConfiguredFinalizer(
        short_name=DEFAULT_FINALIZER_SHORT_NAME,
        name="Default",
        description="",
        settings=app_settings.finalizer,
    )


def configured_finalizers(
    app_settings: ApplicationSettings,
) -> list[ConfiguredFinalizer]:
    """The default finalizer followed by every alternative finalizer."""
    return [_default_finalizer(app_settings)] + [
        ConfiguredFinalizer(
            short_name=alt.id,
            name=alt.name,
            description=alt.description,
            settings=alt.finalizer,
        )
        for alt in app_settings.alternative_finalizers
    ]


def resolve_finalizer(
    app_settings: ApplicationSettings, account_finalizer: str | None
) -> ConfiguredFinalizer:
    """The finalizer an account uses. Accounts without one, or whose alternative
    finalizer has since been removed from the config, use the default."""
    if account_finalizer:
        for alt in app_settings.alternative_finalizers:
            if alt.id == account_finalizer:
                return ConfiguredFinalizer(
                    short_name=alt.id,
                    name=alt.name,
                    description=alt.description,
                    settings=alt.finalizer,
                )

    return _default_finalizer(app_settings)


def calculate_finalizer_thumbprint(
    finalizer_settings: PolymorphicFinalizerSettings,
) -> str:
    """A stable fingerprint of a finalizer's settings. Any change to a setting the
    finalizer lists in thumbprint_attributes(), or to any setting if it lists none,
    changes it. The finalizer type is always included.

    The settings contain credentials and private keys, so this is an HMAC keyed with
    the Django secret key instead of a plain hash, which could be used to guess short
    secrets offline. Rotating the secret key changes every thumbprint."""
    attributes = finalizer_settings.thumbprint_attributes()
    include = None
    if attributes is not None:
        unknown = set(attributes) - set(type(finalizer_settings).model_fields)
        if unknown:
            raise ValueError(
                f"{type(finalizer_settings).__name__} lists unknown thumbprint "
                f"attributes: {', '.join(sorted(unknown))}"
            )
        include = {"type", *attributes}

    canonical = json.dumps(
        finalizer_settings.model_dump(mode="json", include=include),
        sort_keys=True,
        separators=(",", ":"),
    )
    return hmac.new(
        settings.SECRET_KEY.encode(), canonical.encode(), hashlib.sha256
    ).hexdigest()
