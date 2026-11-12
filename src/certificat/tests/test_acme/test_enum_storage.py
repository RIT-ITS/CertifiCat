"""acmev2's statuses and types are (str, Enum) members, whose str() is the
qualified name ("OrderStatus.valid"). They must be stored as their value."""

import pytest
from acmev2.models import (
    AccountStatus,
    AuthorizationStatus,
    ChallengeStatus,
    ChallengeType,
    IdentifierType,
    OrderStatus,
)
from django.db import connection
from django.utils import timezone

from certificat.modules.acme import models as db


def raw_column(model, column: str, pk: int) -> str:
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT {column} FROM {model._meta.db_table} WHERE id = %s", [pk]
        )
        return cursor.fetchone()[0]


@pytest.fixture
def account() -> db.Account:
    return db.Account.objects.create(
        name="enum", status=AccountStatus.valid, jwk="{}", jwk_thumbprint="enum"
    )


@pytest.mark.django_db
def test_create_stores_value(account: db.Account):
    order = db.Order.objects.create(
        account=account,
        name="enum-order",
        status=OrderStatus.pending,
        expires=timezone.now(),
    )
    identifier = db.Identifier.objects.create(
        order=order, type=IdentifierType.dns, value="example.com"
    )
    authz = db.Authorization.objects.create(
        order=order,
        identifier=identifier,
        name="enum-authz",
        status=AuthorizationStatus.pending,
        expires=timezone.now(),
    )
    chall = db.Challenge.objects.create(
        authorization=authz,
        name="enum-chall",
        type=ChallengeType.http_01,
        token="token",
        status=ChallengeStatus.pending,
    )

    assert raw_column(db.Account, "status", account.pk) == "valid"
    assert raw_column(db.Order, "status", order.pk) == "pending"
    assert raw_column(db.Identifier, "type", identifier.pk) == "dns"
    assert raw_column(db.Authorization, "status", authz.pk) == "pending"
    assert raw_column(db.Challenge, "type", chall.pk) == "http-01"
    assert raw_column(db.Challenge, "status", chall.pk) == "pending"

    # The saved instance holds the value too, so it renders the same as a loaded one
    assert type(order.status) is str
    assert str(order.status) == "pending"
    assert str(identifier) == "dns: example.com"


@pytest.mark.django_db
def test_update_and_filter_use_value(account: db.Account):
    db.Account.objects.filter(pk=account.pk).update(status=AccountStatus.deactivated)
    assert raw_column(db.Account, "status", account.pk) == "deactivated"

    assert db.Account.objects.filter(status=AccountStatus.deactivated).exists()
    assert db.Account.objects.filter(
        status__in=[AccountStatus.deactivated, AccountStatus.revoked]
    ).exists()


def test_choices_are_values():
    field = db.Order._meta.get_field("status")
    assert ("valid", "valid") in field.choices
    assert all(type(value) is str for value, _ in field.choices)
