from typing import Self

from acmev2.models import IdentifierType, OrderStatus
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.core.paginator import Page, Paginator
from django.db import models

from certificat.modules.perms import Perms
from certificat.utils import paginate

from .accounts import Account
from .base import Dictable, EnumCharField, TimestampMixin, choices
from .finalizers import FinalizerThumbprint


class OrderQuerySet(models.QuerySet):
    def by_user(self, user: User) -> Self:
        if user.has_perm(Perms.VIEW_ALL_ORDERS):
            return self

        return self.filter(
            models.Q(account__binding__owner=user)
            | models.Q(account__binding__group_scopes__group__in=user.groups.all())
        ).distinct()

    def recent(self, max: int = 10) -> Self:
        return (
            self.order_by("-created_at")
            .prefetch_related("identifiers")
            .distinct()[:max]
        )

    def by_account(self, account: Account) -> Self:
        return (
            self.filter(account=account)
            .prefetch_related("identifiers")
            .distinct()
            .order_by("-created_at")
        )

    def search(self, query: str) -> Self:
        if query:
            query_filter = models.Q()
            for identifier in query.split(","):
                identifier = identifier.strip()
                if identifier.startswith("/") and identifier.endswith("/"):
                    # TODO: Fix this query returning multiple of the same records
                    query_filter |= models.Q(
                        identifiers__value__iregex=identifier[1:-1]
                    )
                else:
                    query_filter |= models.Q(
                        identifiers__value__iexact=identifier.strip()
                    )

            return self.filter(query_filter)

        return self

    def paginated(
        self, curr_page: int | str = 1, per_page: int = 10, order_by="-created_at"
    ) -> tuple[Paginator, Page]:
        return paginate(self.order_by(order_by), curr_page, per_page)


class Order(TimestampMixin, Dictable):
    objects: OrderQuerySet = OrderQuerySet.as_manager()
    dict_fields = ("id", "name", "repr")

    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="orders"
    )

    name = models.CharField(max_length=15, unique=True)
    status = EnumCharField(max_length=15, choices=choices(OrderStatus))
    expires = models.DateTimeField()
    # The finalizer settings used by the latest finalization attempt. Orders from
    # before this was tracked have none.
    finalizer_thumbprint = models.ForeignKey(
        FinalizerThumbprint,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="orders",
    )

    events = GenericRelation("TaggedEvent")

    @property
    def repr(self):
        return f"Order <{self.name}>"

    def accessible_by(self, user: User):
        if user.has_perm(Perms.VIEW_ALL_ORDERS):
            return True

        return self.account.binding.accessible_by(user)

    def __str__(self):
        return self.name

    def last_finalization_error(self):
        return self.finalization_errors.all().order_by("-created_at").first()


class CertificateRequest(TimestampMixin):
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="certificate_request"
    )
    csr = models.TextField()


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

    type = EnumCharField(max_length=15, choices=choices(IdentifierType))
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.type}: {self.value}"
