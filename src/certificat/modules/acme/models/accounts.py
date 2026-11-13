import json
import secrets
import string
from base64 import urlsafe_b64encode
from typing import Self

import inject
import josepy
from acmev2.models import AccountStatus, IdentifierType
from acmev2.services import ACMEEndpoint, IDirectoryService
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.fields import GenericRelation
from django.core.paginator import Page, Paginator
from django.db import models
from django.utils import timezone

from certificat.modules.perms import Perms
from certificat.settings.dynamic import ApplicationSettings
from certificat.utils import paginate

from .base import EnumCharField, TimestampMixin, choices


class Account(TimestampMixin):
    name = models.CharField(max_length=15, unique=True)
    status = EnumCharField(max_length=15, choices=choices(AccountStatus))
    jwk = models.TextField()
    jwk_thumbprint = models.CharField(max_length=100, unique=True)
    finalizer = models.CharField(null=True, blank=True, max_length=255)

    events = GenericRelation("TaggedEvent")

    def __str__(self):
        return self.name

    def josepy_jwk(self) -> josepy.JWK:
        return josepy.JWK.from_json(json.loads(self.jwk))

    def revoke(self):
        self.status = AccountStatus.revoked
        self.save()

    def fully_qualified_name(self):
        directory_service = inject.instance(IDirectoryService)
        return directory_service.url_for(ACMEEndpoint.account, self.name)


class AccountBindingQuerySet(models.QuerySet):
    def by_user(self, user: User) -> Self:
        if user.has_perm(Perms.VIEW_ALL_ACCOUNTS):
            return self

        return self.filter(
            models.Q(owner=user) | models.Q(group_scopes__group__in=user.groups.all())
        )

    def active(self, filter: str | None = None) -> Self:
        queryset = (
            self.filter(
                models.Q(bound_to=None) | models.Q(bound_to__status=AccountStatus.valid)
            )
            .select_related("bound_to", "creator", "owner")
            .prefetch_related("group_scopes", "group_scopes__group")
            .order_by("-created_at")
        ).distinct()

        if filter:
            queryset = queryset.filter(
                models.Q(name__icontains=filter) | models.Q(note__icontains=filter)
            )

        return queryset

    def paginated(
        self, curr_page: int | str = 1, per_page: int = 20, order_by="-created_at"
    ) -> tuple[Paginator, Page]:
        return paginate(self.order_by(order_by), curr_page, per_page)


class AccountBinding(TimestampMixin):
    KID_ENTROPY = string.ascii_lowercase + string.ascii_uppercase + string.digits
    HMAC_ENTROPY = string.ascii_lowercase + string.ascii_uppercase + string.digits
    objects: AccountBindingQuerySet = AccountBindingQuerySet.as_manager()

    hmac_id = models.CharField(max_length=255, unique=True)
    hmac_key = models.CharField(max_length=255)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_bindings",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_bindings",
    )
    bound_to = models.OneToOneField(
        Account, null=True, on_delete=models.CASCADE, related_name="binding"
    )
    bound_at = models.DateTimeField(null=True)
    name = models.CharField(max_length=100)
    note = models.TextField(null=True)

    @classmethod
    def generate(
        cls, creator: User, name: str | None = None, note: str | None = None
    ) -> Self:
        app_settings = inject.instance(ApplicationSettings)

        binding = AccountBinding(
            hmac_id="".join(
                secrets.choice(cls.KID_ENTROPY)
                for _ in range(app_settings.hmac_id_length)
            ),
            hmac_key=urlsafe_b64encode(
                secrets.token_bytes(app_settings.hmac_key_length)
            )
            .decode()
            .rstrip("="),
            creator=creator,
            owner=creator,
            note=note,
            name=name,
        )

        binding.save()
        return binding

    def account_invalid(self) -> bool:
        return self.bound_to and self.bound_to.status != AccountStatus.valid

    def accessible_by(self, user: User) -> bool:
        if user.has_perm(Perms.VIEW_ALL_ACCOUNTS):
            return True

        return (
            user.id == self.owner_id
            or self.group_scopes.filter(group__in=user.groups.all()).count() > 0
        )

    def editable_by(self, user: User) -> bool:
        if user.has_perm(Perms.CHANGE_ALL_ACCOUNTS):
            return True

        return (
            user.id == self.owner_id
            or self.group_scopes.filter(group__in=user.groups.all()).count() > 0
        )

    def transferable_by(self, user: User):
        if user.has_perm(Perms.CHANGE_ALL_ACCOUNTS):
            return True

        return user.id == self.owner_id

    def bind_to(self, account: Account):
        self.bound_to = account
        self.bound_at = timezone.now()

        self.save()


class AccountBindingGroupScope(TimestampMixin):
    binding = models.ForeignKey(
        AccountBinding, on_delete=models.CASCADE, related_name="group_scopes"
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("binding", "group")
        ordering = ("group__name",)


class PreAuthorizedAccountIdentifier(TimestampMixin):
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="preauthorized_identifiers"
    )

    identifier_type = EnumCharField(max_length=15, choices=choices(IdentifierType))
    identifier_value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.identifier_type}: {self.identifier_value}"

    class Meta:
        unique_together = ("account", "identifier_value")
