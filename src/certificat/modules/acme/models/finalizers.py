"""Records of finalizer settings, and state kept by individual finalizers."""

from typing import TYPE_CHECKING, Self

from django.db import models, transaction
from django.utils import timezone

from certificat.modules.acme.finalizers import (
    ConfiguredFinalizer,
    calculate_finalizer_thumbprint,
)

from .base import TimestampMixin

if TYPE_CHECKING:
    from .orders import Order


class FinalizerThumbprintQuerySet(models.QuerySet):
    def active(self) -> FinalizerThumbprintQuerySet:
        return self.filter(deactivated_at__isnull=True)

    def register(
        self, finalizer: ConfiguredFinalizer
    ) -> tuple[FinalizerThumbprint, bool]:
        """Returns the active row for the finalizer's current settings, creating it
        if the settings changed. Returns whether it was created.

        A new row deactivates the finalizer's previous one. Settings that match a
        deactivated row still get a new row, so each row covers one unbroken
        period. A changed name or description is updated in place."""
        thumbprint = calculate_finalizer_thumbprint(finalizer.settings)
        with transaction.atomic():
            active = list(
                self.active()
                .filter(short_name=finalizer.short_name)
                .select_for_update()
                .order_by("-activated_at", "-id")
            )
            current = next((r for r in active if r.thumbprint == thumbprint), None)

            now = timezone.now()
            # Normally at most one row is active. Anything else left active by
            # concurrent registrations is closed here too.
            stale = [r.pk for r in active if r is not current]
            if stale:
                self.filter(pk__in=stale).update(deactivated_at=now, updated_at=now)

            if current is None:
                return self.create(
                    short_name=finalizer.short_name,
                    name=finalizer.name,
                    description=finalizer.description,
                    type=finalizer.settings.type,
                    thumbprint=thumbprint,
                    activated_at=now,
                ), True

        if (current.name, current.description) != (
            finalizer.name,
            finalizer.description,
        ):
            current.name = finalizer.name
            current.description = finalizer.description
            current.save(update_fields=["name", "description", "updated_at"])

        return current, False

    def deactivate_unconfigured(self, short_names: list[str]) -> int:
        """Deactivates finalizers that are no longer in the config. Returns how
        many were deactivated."""
        now = timezone.now()
        return (
            self.active()
            .exclude(short_name__in=short_names)
            .update(deactivated_at=now, updated_at=now)
        )


class FinalizerThumbprint(TimestampMixin):
    """
    Creates thumbprints for finalizers defined in the startup.
    The purpose of this is to create a snapshot of finalizers that
    tracks when they changed so information can be stored at order-time
    of what finalizer was used.
    """

    objects: FinalizerThumbprintQuerySet = FinalizerThumbprintQuerySet.as_manager()

    short_name = models.CharField(max_length=100)
    name = models.TextField()
    description = models.TextField()
    # The finalizer's type setting, e.g. "local" or "acme"
    type = models.CharField(max_length=50)
    thumbprint = models.CharField(max_length=100)
    # The period these settings were in use. Empty while they still are.
    activated_at = models.DateTimeField(default=timezone.now)
    deactivated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [  # noqa: RUF012
            models.Index(
                fields=["short_name", "deactivated_at"],
                name="finalizer_thumbprint_active",
            ),
        ]

    def __str__(self):
        return f"{self.short_name} ({self.thumbprint[:12]})"


class ACMEFinalizerBinding(TimestampMixin):
    directory = models.URLField()
    account_id = models.URLField()
    key_id = models.CharField(max_length=255, null=True)
    private_key = models.TextField()

    def get(**kwargs) -> Self | None:
        try:
            return ACMEFinalizerBinding.objects.get(**kwargs)
        except ACMEFinalizerBinding.DoesNotExist:
            return None

    def __str__(self):
        return f"{self.account_id}"


class SectigoOrderProcessingState(TimestampMixin):
    class Choices(models.TextChoices):
        SUBMITTED = "SU", "Submitted"
        ENROLLED = "EN", "Enrolled"
        APPROVED = "AP", "Approved"
        COLLECTED = "CO", "Collected"

    order = models.ForeignKey("acme.Order", on_delete=models.CASCADE)
    ssl_id = models.CharField(null=True, max_length=50)
    state = models.CharField(
        max_length=2,
        choices=Choices,
        default=Choices.SUBMITTED,
    )

    @classmethod
    def for_order(cls, order: Order) -> SectigoOrderProcessingState:
        state, _ = SectigoOrderProcessingState.objects.get_or_create(order=order)
        return state

    def transition_to(self, choice: Choices):
        self.state = choice
        self.save()


class CertiNextOrderProcessingState(TimestampMixin):
    class Choices(models.TextChoices):
        SUBMITTED = "SU", "Submitted"
        ORDERED = "OR", "Ordered"
        FULFILLED = "FU", "Fulfilled"
        COLLECTED = "CO", "Collected"
        ERRORED = "ER", "Errored"

    order = models.ForeignKey("acme.Order", on_delete=models.CASCADE)
    order_number = models.CharField(null=True, max_length=50)
    state = models.CharField(
        max_length=2,
        choices=Choices,
        default=Choices.SUBMITTED,
    )

    @classmethod
    def for_order(cls, order: Order) -> CertiNextOrderProcessingState:
        state, _ = CertiNextOrderProcessingState.objects.get_or_create(order=order)
        return state

    def transition_to(self, choice: Choices):
        self.state = choice
        self.save()
