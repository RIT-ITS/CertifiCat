from pydantic import BaseModel, Field
from acmev2.models import (
    AccountResource,
    OrderResource,
    AuthorizationResource,
    HTTPChallengeResource,
    CertResource,
    Identifier,
)


class WithDjangoData:
    model_id: int | None = Field(exclude=True, default=None)


class DjangoBaseModel(BaseModel, WithDjangoData):
    pass


class DjangoAccountResource(AccountResource, WithDjangoData):
    pass


class DjangoOrderResource(OrderResource, WithDjangoData):
    pass


class DjangoAuthorizationResource(AuthorizationResource, WithDjangoData):
    pass


class DjangoHTTPChallengeResource(HTTPChallengeResource, WithDjangoData):
    pass


class DjangoIdentifierResource(Identifier, WithDjangoData):
    pass


class DjangoCertResource(CertResource, WithDjangoData):
    pass
