from typing import Self

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from pydantic import BaseModel

from certificat.modules.html.contextvars import request_context

from .accounts import AccountBinding


class OrderEventType(models.TextChoices):
    CREATED = "ord.Created", "Order created"
    STATUS_UPDATED = "ord.StatUpdate", "Order status update"
    FINALIZATION_QUEUED = "ord.FinQueued", "Order finalization queued"
    FINALIZATION_PASSED = "ord.FinPassed", "Order finalized"
    FINALIZATION_ERROR = "ord.FinErr", "Order finalization error"
    FINALIZATION_FAILED = "ord.FinFailed", "Order finalization failed"


class AccountEventType(models.TextChoices):
    BOUND = "acct.Bound", "Account bound"


class AuthorizationEventType(models.TextChoices):
    PREAUTHORIZED = "auth.Preauth", "Preauthorized identifier"
    CREATED = "auth.Created", "Authorization created"
    STATUS_UPDATED = "auth.StatUpdate", "Authorization status update"


class ChallengeEventType(models.TextChoices):
    CREATED = "chall.Created", "Challenge created"
    STATUS_UPDATED = "chall.StatUpdate", "Challenge status update"
    VALIDATION_QUEUED = "chall.ValQueued", "Challenge validation queued"
    VALIDATION_PASSED = "chall.ValPassed", "Challenge validation passed"
    VALIDATION_FAILED = "chall.ValFailed", "Challenge validation failed"


ALL_EVENT_CHOICES = (
    OrderEventType.choices
    + AccountEventType.choices
    + AuthorizationEventType.choices
    + ChallengeEventType.choices
)

ALL_EVENT_CHOICES_DICT = {c[0]: c[1] for c in ALL_EVENT_CHOICES}


class TaggedEventQuerySet(models.QuerySet):
    def related_to(self, model: BaseModel) -> Self:
        return self.filter(
            content_type=ContentType.objects.get_for_model(model.__class__),
            object_id=model.pk,
        )

    def bound_to_event(self, binding: AccountBinding) -> TaggedEvent | None:
        if binding.bound_to:
            return (
                self.related_to(binding.bound_to)
                .filter(event_type=AccountEventType.BOUND)
                .first()
            )
        else:
            return None


class TaggedEvent(models.Model):
    objects: TaggedEventQuerySet = TaggedEventQuerySet.as_manager()

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

    @classmethod
    def record_by_type(cls, event: str, object_type: type, object_id: int, **kwargs):
        evt = TaggedEvent(
            content_type=ContentType.objects.get_for_model(object_type),
            object_id=object_id,
            event_type=event,
            **kwargs,
        )
        evt.save()
        return evt

    def get_event_type_display(self):
        return ALL_EVENT_CHOICES_DICT.get(self.event_type)

    def save(self, *args, **kwargs):
        req = request_context.get()

        if req:
            x_forwarded_for = req.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                ip = x_forwarded_for.split(",")[0]
            else:
                ip = req.META.get("REMOTE_ADDR")

        defaults = {
            "ip_address": ip if req else None,
            "triggered_by": req.user if req and not req.user.is_anonymous else None,
            "user_agent": req.META.get("HTTP_USER_AGENT") if req else None,
        }

        for key, value in defaults.items():
            if getattr(self, key) is None:
                setattr(self, key, value)

        super().save(*args, **kwargs)

    class Meta:
        ordering = ("-created_at",)
        indexes = [  # noqa: RUF012
            models.Index(fields=["event_type"]),
            models.Index(fields=["content_type", "object_id"]),
        ]
