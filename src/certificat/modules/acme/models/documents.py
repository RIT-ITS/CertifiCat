from django.db import models

from .base import TimestampMixin


class MarkdownDisplay(TimestampMixin):
    text = models.TextField()

    class Meta:
        abstract = True


class Usage(MarkdownDisplay):
    pass


class TermsOfService(MarkdownDisplay):
    pass
