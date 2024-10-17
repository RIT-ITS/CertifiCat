from enum import Enum
import json
from typing import Mapping
from django.db import models
from acmev2.models import (
    AccountStatus,
    OrderStatus,
    IdentifierType,
    AccountResource,
    AuthorizationStatus,
    ChallengeType,
    OrderResource,
    Identifier as IdentifierResource,
    AuthorizationResource,
    ChallengeStatus,
    HTTPChallengeResource,
    CertResource,
)
from pydantic import BaseModel
from josepy import JWK
from django.utils.timezone import make_naive


def choices(obj: Enum) -> Mapping[str, str]:
    return {s: s for s in obj}


class TimestampMixin:
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Account(models.Model, TimestampMixin):
    name = models.CharField(max_length=15, unique=True)
    status = models.CharField(max_length=15, choices=choices(AccountStatus))
    jwk = models.TextField()
    jwk_thumbprint = models.CharField(max_length=100, unique=True)


class Order(models.Model, TimestampMixin):
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="orders"
    )

    name = models.CharField(max_length=15, unique=True)
    status = models.CharField(max_length=15, choices=choices(OrderStatus))
    expires = models.DateTimeField()


class CertificateRequest(models.Model, TimestampMixin):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    csr = models.TextField()


class Certificate(models.Model, TimestampMixin):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    chain = models.TextField()


class Identifier(models.Model, TimestampMixin):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="identifiers"
    )

    type = models.CharField(max_length=15, choices=choices(IdentifierType))
    value = models.CharField(max_length=255)


class Authorization(models.Model, TimestampMixin):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="authorizations"
    )
    identifier = models.ForeignKey(
        Identifier, on_delete=models.CASCADE, related_name="authorizations"
    )

    name = models.CharField(max_length=15, unique=True)
    status = models.CharField(max_length=15, choices=choices(AuthorizationStatus))
    expires = models.DateTimeField()


class Challenge(models.Model, TimestampMixin):
    authorization = models.ForeignKey(
        Authorization, on_delete=models.CASCADE, related_name="challenges"
    )

    name = models.CharField(max_length=15, unique=True)
    type = models.CharField(max_length=15, choices=choices(ChallengeType))
    token = models.CharField(max_length=100)
    status = models.CharField(max_length=15, choices=choices(ChallengeStatus))
    validated = models.DateTimeField(null=True)


class OrderProcessingState(models.Model):
    class Choices(models.TextChoices):
        SUBMITTED = "SU", "Submitted"
        ENROLLED = "EN", "Enrolled"
        APPROVED = "AP", "Approved"
        COLLECTED = "CO", "Collected"

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    ssl_id = models.CharField(null=True, max_length=50)
    state = models.CharField(
        max_length=2,
        choices=Choices,
        default=Choices.SUBMITTED,
    )

    @classmethod
    def for_order(cls, order: Order) -> "OrderProcessingState":
        state, _ = OrderProcessingState.objects.get_or_create(order=order)
        return state

    def transition_to(self, choice: Choices):
        self.state = choice
        self.save()


def to_pydantic(model: models.Model) -> BaseModel:
    match model:
        case Account():
            return AccountResource(
                id=model.name,
                status=model.status,
                # Terms of service have to be agreed to for an entry
                # to be in the database
                termsOfServiceAgreed=True,
                jwk=JWK.from_json(json.loads(model.jwk)),
            )
        case Order():
            return OrderResource(
                id=model.name,
                account_id=model.account.name,
                status=model.status,
                expires=make_naive(model.expires),
                identifiers=[to_pydantic(i) for i in model.identifiers.all()],
                authorizations=[to_pydantic(a) for a in model.authorizations.all()],
            )
        case Authorization():
            return AuthorizationResource(
                id=model.name,
                order_id=model.order.name,
                status=model.status,
                expires=make_naive(model.expires),
                identifier=to_pydantic(model.identifier),
                challenges=[to_pydantic(c) for c in model.challenges.all()],
            )
        case Challenge():
            return HTTPChallengeResource(
                id=model.name,
                authz_id=model.authorization.name,
                type=model.type,
                token=model.token,
                status=model.status,
                validated=make_naive(model.validated) if model.validated else None,
            )
        case Identifier():
            return IdentifierResource(id=model.id, type=model.type, value=model.value)
        case Certificate():
            return CertResource(id=model.order.name, pem=model.chain)
        case _:
            raise Exception(
                f"Error converting model {model} to pydantic representation"
            )
