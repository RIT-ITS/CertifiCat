import json
import random
import string
from enum import Enum
from typing import List, Mapping, Self

from django.core.serializers.json import DjangoJSONEncoder
import cryptography
import cryptography.x509
import cryptography.x509.extensions
import inject
from acmev2.models import (
    AccountResource,
    AccountStatus,
    AuthorizationResource,
    AuthorizationStatus,
    CertResource,
    ChallengeStatus,
    ChallengeType,
    HTTPChallengeResource,
    IdentifierType,
    OrderResource,
    OrderStatus,
)
from acmev2.models import (
    Identifier as IdentifierResource,
)
from acmev2.services import IDirectoryService, ACMEEndpoint
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.db import models
from django.utils import timezone
from django.utils.timezone import make_naive
from josepy import JWK
from pydantic import BaseModel
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from cryptography import x509
from certificat.settings.dynamic import ApplicationSettings
from certificat.modules.html.contextvars import request_context
from datetime import datetime


def choices(obj: Enum) -> Mapping[str, str]:
    return {s: s for s in obj}


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Account(TimestampMixin):
    name = models.CharField(max_length=15, unique=True)
    status = models.CharField(max_length=15, choices=choices(AccountStatus))
    jwk = models.TextField()
    jwk_thumbprint = models.CharField(max_length=100, unique=True)

    events = GenericRelation("TaggedEvent")

    def revoke(self):
        self.status = AccountStatus.revoked
        self.save()

    def fully_qualified_name(self):
        directory_service = inject.instance(IDirectoryService)
        return directory_service.url_for(ACMEEndpoint.account, self.name)


class AccountBindingManager(models.Manager):
    def by_user(self, user: User):
        if user.is_superuser:
            return self

        return self.filter(
            models.Q(creator=user) | models.Q(group_scopes__group__in=user.groups.all())
        )


class AccountBinding(TimestampMixin):
    KID_ENTROPY = string.ascii_lowercase + string.ascii_uppercase + string.digits
    HMAC_ENTROPY = string.ascii_lowercase + string.ascii_uppercase + string.digits
    objects = AccountBindingManager()

    hmac_id = models.CharField(max_length=255, unique=True)
    hmac_key = models.CharField(max_length=255)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    bound_to = models.OneToOneField(
        Account, null=True, on_delete=models.CASCADE, related_name="binding"
    )
    bound_at = models.DateTimeField(null=True)
    name = models.CharField(max_length=100)
    note = models.TextField(null=True)

    @classmethod
    def generate(cls, creator: User, name: str = None, note: str = None) -> Self:
        app_settings = inject.instance(ApplicationSettings)

        binding = AccountBinding(
            hmac_id="".join(
                random.choices(cls.KID_ENTROPY, k=app_settings.hmac_id_length)
            ),
            hmac_key="".join(
                random.choices(cls.HMAC_ENTROPY, k=app_settings.hmac_key_length)
            ),
            creator=creator,
            note=note,
            name=name,
        )

        binding.save()
        return binding

    def accessible_by(self, user: User):
        if user.is_superuser:
            return True

        return user.id == self.creator_id or self.group_scopes.filter(
            group__in=user.groups.all()
        )

    def bind_to(self, account: Account):
        self.bound_to = account
        self.bound_at = timezone.now()

        self.save()


class AccountBindingGroupScope(TimestampMixin):
    binding = models.ForeignKey(
        AccountBinding, on_delete=models.CASCADE, related_name="group_scopes"
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def friendly_name(self):
        return self.group.name

    class Meta:
        unique_together = ("binding", "group")


class Order(TimestampMixin):
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="orders"
    )

    name = models.CharField(max_length=15, unique=True)
    status = models.CharField(max_length=15, choices=choices(OrderStatus))
    expires = models.DateTimeField()

    events = GenericRelation("TaggedEvent")

    def last_finalization_error(self):
        return self.finalization_errors.all().order_by("-created_at").first()


class CertificateRequest(TimestampMixin):
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="certificate_request"
    )
    csr = models.TextField()


class CertificateMetadata(BaseModel):
    version: int
    not_valid_before: datetime
    not_valid_after: datetime
    sans: List[str]


class Certificate(TimestampMixin):
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="certificate"
    )
    metadata = models.JSONField(null=True, encoder=DjangoJSONEncoder)
    chain = models.TextField()

    def save(self, *args, **kwargs):
        if self.metadata is None:
            self.rebuild_metadata()

        return super().save(*args, **kwargs)

    def rebuild_metadata(self):
        metadata_version = 1
        if not self.metadata or self.metadata.get("version") != metadata_version:
            certs = x509.load_pem_x509_certificates(self.chain.encode())
            leaf_cert = certs[0]
            try:
                san_extension = leaf_cert.extensions.get_extension_for_class(
                    x509.SubjectAlternativeName
                )
                sans = [v.value for v in san_extension.value]
            except cryptography.x509.extensions.ExtensionNotFound:
                sans = []

            metadata = CertificateMetadata(
                version=metadata_version,
                not_valid_before=leaf_cert.not_valid_before_utc,
                not_valid_after=leaf_cert.not_valid_after_utc,
                sans=sans,
            )

            self.metadata = metadata.model_dump()


class OrderFinalizationError(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="finalization_errors"
    )
    error = models.TextField()


class Identifier(TimestampMixin):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="identifiers"
    )

    type = models.CharField(max_length=15, choices=choices(IdentifierType))
    value = models.CharField(max_length=255)


class Authorization(TimestampMixin):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="authorizations"
    )
    identifier = models.ForeignKey(
        Identifier, on_delete=models.CASCADE, related_name="authorizations"
    )

    name = models.CharField(max_length=15, unique=True)
    status = models.CharField(max_length=15, choices=choices(AuthorizationStatus))
    expires = models.DateTimeField()

    def is_valid(self):
        return self.status == AuthorizationStatus.valid

    def first_valid_challenge(self):
        for chall in self.challenges.all():
            if chall.status == ChallengeStatus.valid:
                return chall

    def first_invalid_challenge(self):
        for chall in self.challenges.all():
            if chall.status == ChallengeStatus.invalid:
                return chall


class Challenge(TimestampMixin):
    authorization = models.ForeignKey(
        Authorization, on_delete=models.CASCADE, related_name="challenges"
    )

    name = models.CharField(max_length=15, unique=True)
    type = models.CharField(max_length=15, choices=choices(ChallengeType))
    token = models.CharField(max_length=100)
    status = models.CharField(max_length=15, choices=choices(ChallengeStatus))
    validated = models.DateTimeField(null=True)

    def first_error(self):
        query = self.errors.all()
        if query._result_cache:
            return query[0] if len(query) > 0 else None
        return query.first()


class ChallengeError(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    challenge = models.ForeignKey(
        Challenge, on_delete=models.CASCADE, related_name="errors"
    )
    error = models.TextField()


class SectigoOrderProcessingState(TimestampMixin):
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
    def for_order(cls, order: Order) -> "SectigoOrderProcessingState":
        state, _ = SectigoOrderProcessingState.objects.get_or_create(order=order)
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


class OrderEventType(models.TextChoices):
    CREATED = "ord.Created", "Order created"


class AccountEventType(models.TextChoices):
    BOUND = "acct.Bound", "Account bound"


class TaggedEvent(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(null=True)
    event_type = models.CharField(max_length=20)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    payload = models.JSONField(null=True)

    @classmethod
    def record(cls, event: str, obj: models.Model, **kwargs):
        evt = TaggedEvent(content_object=obj, event_type=event, **kwargs)
        evt.save()

        return evt

    def save(self, *args, **kwargs):
        req = request_context.get()

        x_forwarded_for = req.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = req.META.get("REMOTE_ADDR")

        defaults = {
            "ip_address": ip,
            "triggered_by": req.user if req and not req.user.is_anonymous else None,
            "user_agent": req.META.get("HTTP_USER_AGENT") if req else None,
        }

        for key, value in defaults.items():
            if getattr(self, key) is None:
                setattr(self, key, value)

        super().save(*args, **kwargs)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["event_type"]),
            models.Index(fields=["content_type", "object_id"]),
        ]
