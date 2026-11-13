import inject
import pytest
from acmev2.models import AccountStatus, OrderStatus
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from certificat.modules.acme import models as db
from certificat.modules.acme.backends import NotReadyException
from certificat.modules.acme.finalizers import (
    DEFAULT_FINALIZER_SHORT_NAME,
    ConfiguredFinalizer,
    calculate_finalizer_thumbprint,
    configured_finalizers,
)
from certificat.modules.tasks import finalize_order
from certificat.settings.dynamic import (
    ACMEFinalizerSettings,
    AlternativeFinalizerSettings,
    ApplicationSettings,
    LocalFinalizerSettings,
)

from ..helpers import do_challenge
from ..helpers import finalize_order as finalize_acme_order


def acme_settings(**overrides) -> ACMEFinalizerSettings:
    return ACMEFinalizerSettings(
        **{
            "directory": "https://acme.edu/directory",
            "account_kid": "kid",
            "account_hmac_key": "hmac",
            "account_email": "noreply@acme.edu",
        }
        | overrides
    )


def configured(settings=None, short_name="alt", name="Alt", description="d"):
    return ConfiguredFinalizer(
        short_name=short_name,
        name=name,
        description=description,
        settings=settings or acme_settings(),
    )


@pytest.fixture
def app_settings(monkeypatch) -> ApplicationSettings:
    settings = inject.instance(ApplicationSettings)
    # Tests change these, restore them afterwards
    monkeypatch.setattr(settings, "alternative_finalizers", [])
    monkeypatch.setattr(settings, "finalizer", settings.finalizer.model_copy())
    return settings


def test_thumbprint_is_stable_and_tracks_listed_settings():
    first = calculate_finalizer_thumbprint(acme_settings())
    assert first == calculate_finalizer_thumbprint(acme_settings())
    assert len(first) == 64

    # ACMEFinalizerSettings.thumbprint_attributes() lists these, secrets included
    assert first != calculate_finalizer_thumbprint(acme_settings(account_kid="other"))
    assert first != calculate_finalizer_thumbprint(
        acme_settings(account_hmac_key="other")
    )
    # and leaves these out
    assert first == calculate_finalizer_thumbprint(
        acme_settings(account_email="other@acme.edu", finalization_timeout=91)
    )


def test_thumbprint_is_keyed_with_secret_key(settings):
    first = calculate_finalizer_thumbprint(acme_settings())
    settings.SECRET_KEY = "a different secret key"
    assert first != calculate_finalizer_thumbprint(acme_settings())


def test_thumbprint_uses_listed_attributes(monkeypatch):
    monkeypatch.setattr(
        ACMEFinalizerSettings,
        "thumbprint_attributes",
        lambda self: ["directory", "account_kid"],
    )
    first = calculate_finalizer_thumbprint(acme_settings())

    # Unlisted settings are ignored
    assert first == calculate_finalizer_thumbprint(
        acme_settings(account_hmac_key="other", finalization_timeout=91)
    )
    assert first != calculate_finalizer_thumbprint(acme_settings(account_kid="other"))
    # Including every attribute gives a different thumbprint
    monkeypatch.setattr(
        ACMEFinalizerSettings, "thumbprint_attributes", lambda self: None
    )
    assert first != calculate_finalizer_thumbprint(acme_settings())


def test_thumbprint_always_includes_type(monkeypatch):
    for klass in (ACMEFinalizerSettings, LocalFinalizerSettings):
        monkeypatch.setattr(klass, "thumbprint_attributes", lambda self: [])
    local = LocalFinalizerSettings(key="k", cert="c")
    assert calculate_finalizer_thumbprint(acme_settings()) != (
        calculate_finalizer_thumbprint(local)
    )


def test_thumbprint_rejects_unknown_attributes(monkeypatch):
    monkeypatch.setattr(
        ACMEFinalizerSettings, "thumbprint_attributes", lambda self: ["nope"]
    )
    with pytest.raises(ValueError, match="nope"):
        calculate_finalizer_thumbprint(acme_settings())


@pytest.mark.django_db
def test_register():
    record, created = db.FinalizerThumbprint.objects.register(configured())
    assert created
    assert (record.short_name, record.name, record.type) == ("alt", "Alt", "acme")
    assert record.activated_at is not None
    assert record.deactivated_at is None

    # Same settings, nothing new
    again, created = db.FinalizerThumbprint.objects.register(configured())
    assert not created
    assert again.pk == record.pk

    # Name and description are updated in place
    renamed, created = db.FinalizerThumbprint.objects.register(
        configured(name="Renamed", description="new")
    )
    assert not created
    assert renamed.pk == record.pk
    record.refresh_from_db()
    assert (record.name, record.description) == ("Renamed", "new")

    # A settings change deactivates the old row and starts a new one
    changed, created = db.FinalizerThumbprint.objects.register(
        configured(acme_settings(account_kid="other"))
    )
    assert created
    assert changed.pk != record.pk
    record.refresh_from_db()
    assert record.deactivated_at == changed.activated_at
    assert changed.deactivated_at is None

    # The same settings under another finalizer are tracked separately
    other, created = db.FinalizerThumbprint.objects.register(
        configured(short_name="other")
    )
    assert created
    assert other.deactivated_at is None
    assert db.FinalizerThumbprint.objects.active().count() == 2


@pytest.mark.django_db
def test_reverting_settings_is_a_new_period():
    original, _ = db.FinalizerThumbprint.objects.register(configured())
    changed, _ = db.FinalizerThumbprint.objects.register(
        configured(acme_settings(account_kid="other"))
    )

    reverted, created = db.FinalizerThumbprint.objects.register(configured())
    assert created
    assert reverted.pk != original.pk
    assert reverted.thumbprint == original.thumbprint

    original.refresh_from_db()
    changed.refresh_from_db()
    assert original.activated_at < original.deactivated_at
    assert changed.deactivated_at == reverted.activated_at
    assert list(db.FinalizerThumbprint.objects.active()) == [reverted]


@pytest.mark.django_db
def test_register_closes_duplicate_active_rows():
    # Left behind if two processes register a new finalizer at the same time
    for _ in range(2):
        db.FinalizerThumbprint.objects.create(
            short_name="alt",
            name="Alt",
            description="d",
            type="acme",
            thumbprint=calculate_finalizer_thumbprint(acme_settings()),
        )

    record, created = db.FinalizerThumbprint.objects.register(configured())
    assert not created
    assert list(db.FinalizerThumbprint.objects.active()) == [record]


@pytest.mark.django_db
def test_register_finalizers_command(app_settings: ApplicationSettings):
    app_settings.alternative_finalizers = [
        AlternativeFinalizerSettings(
            id="alt", name="Alt", description="d", finalizer=acme_settings()
        )
    ]

    call_command("register_finalizers")
    call_command("register_finalizers")

    rows = db.FinalizerThumbprint.objects.order_by("short_name")
    assert [(r.short_name, r.type, r.deactivated_at) for r in rows] == [
        ("alt", "acme", None),
        (DEFAULT_FINALIZER_SHORT_NAME, app_settings.finalizer.type, None),
    ]
    assert len(configured_finalizers(app_settings)) == 2

    # Removing a finalizer from the config deactivates it
    app_settings.alternative_finalizers = []
    call_command("register_finalizers")
    assert [r.short_name for r in db.FinalizerThumbprint.objects.active()] == [
        DEFAULT_FINALIZER_SHORT_NAME
    ]
    assert db.FinalizerThumbprint.objects.get(short_name="alt").deactivated_at


@pytest.mark.django_db
@pytest.mark.parametrize("use_alternative", [False, True])
def test_finalized_order_is_linked(
    app_settings: ApplicationSettings, acme_client, acme_neworder, use_alternative
):
    # The alternative is a copy of the test's local finalizer so it can issue certs
    app_settings.alternative_finalizers = [
        AlternativeFinalizerSettings(
            id="alt",
            name="Alt",
            description="d",
            finalizer=app_settings.finalizer.model_copy(),
        )
    ]

    new_order = acme_neworder()
    order = db.Order.objects.get(name=new_order.response.uri.split("/")[-1])
    if use_alternative:
        order.account.finalizer = "alt"
        order.account.save()

    finalized = finalize_acme_order(
        acme_client, do_challenge(acme_client, new_order.response)
    )
    assert finalized.body.status.name == "valid"

    order.refresh_from_db()
    expected = "alt" if use_alternative else DEFAULT_FINALIZER_SHORT_NAME
    assert order.finalizer_thumbprint.short_name == expected
    assert order.finalizer_thumbprint.thumbprint == calculate_finalizer_thumbprint(
        app_settings.finalizer
    )


@pytest.mark.django_db
def test_each_attempt_overwrites_link(app_settings: ApplicationSettings, mocker):
    account = db.Account.objects.create(
        name="thumb", status=AccountStatus.valid, jwk="{}", jwk_thumbprint="thumb"
    )
    # A finalizer that was removed from the config falls back to the default
    account.finalizer = "removed"
    account.save()
    order = db.Order.objects.create(
        account=account,
        name="thumb-order",
        status=OrderStatus.processing,
        expires=timezone.now(),
    )
    db.CertificateRequest.objects.create(order=order, csr="unused")

    finalizer = mocker.Mock()
    finalizer.finalize.side_effect = NotReadyException
    mocker.patch.object(finalize_order, "build_finalizer", return_value=finalizer)

    assert not finalize_order._run_task(order.name)
    order.refresh_from_db()
    first = order.finalizer_thumbprint
    assert first.short_name == DEFAULT_FINALIZER_SHORT_NAME

    # The config changes between retries
    app_settings.finalizer.module = app_settings.finalizer.module + "Changed"
    assert not finalize_order._run_task(order.name)
    order.refresh_from_db()
    assert order.finalizer_thumbprint.pk != first.pk
    assert order.finalizer_thumbprint.thumbprint == calculate_finalizer_thumbprint(
        app_settings.finalizer
    )


@pytest.mark.django_db
def test_order_page_shows_settings_period(web_client: Client, gen_bound_client):
    record, _ = db.FinalizerThumbprint.objects.register(configured())
    _, registration, _ = gen_bound_client()
    account = db.Account.objects.get(name=registration.uri.split("/")[-1])
    order = db.Order.objects.create(
        account=account,
        name="page-order",
        status=OrderStatus.valid,
        expires=timezone.now(),
        finalizer_thumbprint=record,
    )
    web_client.force_login(
        User.objects.create_superuser("thumb-admin", password="unused")
    )
    url = reverse("order", args=[order.id])

    response = web_client.get(url)
    assert response.status_code == 200
    assert response.context["order"].finalizer_thumbprint == record
    assert "Detected" in response.text
    assert "&mdash; present" in response.text

    # Once the settings change, the period has an end
    db.FinalizerThumbprint.objects.register(
        configured(acme_settings(account_kid="other"))
    )
    response = web_client.get(url)
    assert "Detected" in response.text
    assert "&mdash; present" not in response.text
