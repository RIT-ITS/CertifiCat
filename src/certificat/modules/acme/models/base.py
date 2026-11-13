import operator
from collections.abc import Mapping
from enum import Enum

from django.db import models


class Dictable:
    dict_fields = ("id",)

    def to_dict(self):
        return {name: operator.attrgetter(name)(self) for name in self.dict_fields}


def choices(obj: type[Enum]) -> Mapping[str, str]:
    # Use the raw values. str() of a (str, Enum) member is the qualified name
    # ("OrderStatus.valid"), which forms and the Django admin would submit.
    return {s.value: s.value for s in obj}


class EnumCharField(models.CharField):
    """A CharField that stores acmev2's (str, Enum) members by value.

    Those enums mix in str, so Django passes them to the database driver as-is and
    the driver formats them with str(), which gives the qualified member name
    ("OrderStatus.valid") rather than "valid". This converts members to their value
    for saves, .update() calls, and lookups.
    """

    def get_prep_value(self, value):
        if isinstance(value, Enum):
            value = value.value
        return super().get_prep_value(value)

    def pre_save(self, model_instance, add):
        value = super().pre_save(model_instance, add)
        if isinstance(value, Enum):
            # Keep the instance consistent with what was stored
            value = value.value
            setattr(model_instance, self.attname, value)
        return value

    def deconstruct(self):
        # Behaves the same as a CharField in the database, so don't make migrations
        # depend on this class
        name, _, args, kwargs = super().deconstruct()
        return name, "django.db.models.CharField", args, kwargs


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
