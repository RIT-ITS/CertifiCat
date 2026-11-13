import json

from django.db import models
from django.utils.timezone import make_naive
from josepy import JWK

from certificat.modules.acme.pydantic import (
    DjangoAccountResource,
    DjangoAuthorizationResource,
    DjangoBaseModel,
    DjangoCertResource,
    DjangoHTTPChallengeResource,
    DjangoIdentifierResource,
    DjangoOrderResource,
)

from .accounts import Account
from .authorizations import Authorization, Challenge
from .certificates import Certificate
from .orders import Identifier, Order


def to_pydantic(model: models.Model) -> DjangoBaseModel:
    match model:
        case Account():
            return DjangoAccountResource(
                model_id=model.id,
                id=model.name,
                status=model.status,
                # Terms of service have to be agreed to for an entry
                # to be in the database
                termsOfServiceAgreed=True,
                jwk=JWK.from_json(json.loads(model.jwk)),
            )
        case Order():
            return DjangoOrderResource(
                model_id=model.id,
                id=model.name,
                account_id=model.account.name,
                status=model.status,
                expires=make_naive(model.expires),
                identifiers=[to_pydantic(i) for i in model.identifiers.all()],
                authorizations=[to_pydantic(a) for a in model.authorizations.all()],
            )
        case Authorization():
            return DjangoAuthorizationResource(
                model_id=model.id,
                id=model.name,
                order_id=model.order.name,
                status=model.status,
                expires=make_naive(model.expires),
                identifier=to_pydantic(model.identifier),
                challenges=[to_pydantic(c) for c in model.challenges.all()],
            )
        case Challenge():
            return DjangoHTTPChallengeResource(
                model_id=model.id,
                id=model.name,
                authz_id=model.authorization.name,
                type=model.type,
                token=model.token,
                status=model.status,
                validated=make_naive(model.validated) if model.validated else None,
            )
        case Identifier():
            return DjangoIdentifierResource(
                model_id=model.id, id=model.id, type=model.type, value=model.value
            )
        case Certificate():
            return DjangoCertResource(
                model_id=model.id, id=model.order.name, pem=model.chain
            )
        case _:
            raise Exception(  # noqa: TRY002
                f"Error converting model {model} to pydantic representation"
            )
