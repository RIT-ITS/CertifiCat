from acmev2.models import AuthorizationStatus, ChallengeStatus, ChallengeType
from django.db import models

from .base import Dictable, EnumCharField, TimestampMixin, choices
from .orders import Identifier, Order


class Authorization(TimestampMixin, Dictable):
    dict_fields = ("id", "name", "repr")
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="authorizations"
    )
    identifier = models.ForeignKey(
        Identifier, on_delete=models.CASCADE, related_name="authorizations"
    )

    name = models.CharField(max_length=15, unique=True)
    status = EnumCharField(max_length=15, choices=choices(AuthorizationStatus))
    expires = models.DateTimeField()

    @property
    def repr(self):
        return f"Authorization <{self.name}>"

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


class Challenge(TimestampMixin, Dictable):
    dict_fields = ("id", "name", "repr")
    authorization = models.ForeignKey(
        Authorization, on_delete=models.CASCADE, related_name="challenges"
    )

    name = models.CharField(max_length=15, unique=True)
    type = EnumCharField(max_length=15, choices=choices(ChallengeType))
    token = models.CharField(max_length=100)
    status = EnumCharField(max_length=15, choices=choices(ChallengeStatus))
    validated = models.DateTimeField(null=True)

    @property
    def repr(self):
        return f"Challenge <{self.name}>"

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
