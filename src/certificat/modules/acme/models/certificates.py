from datetime import datetime
from typing import Self

import cryptography
import cryptography.x509
import cryptography.x509.extensions
from cryptography import x509
from django.core.paginator import Page, Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from pydantic import BaseModel

from certificat.utils import paginate

from .base import Dictable, TimestampMixin
from .orders import Order


class CertificateMetadata(BaseModel):
    version: int
    not_valid_before: datetime
    not_valid_after: datetime
    sans: list[str]


class CertificateQuerySet(models.QuerySet):
    def recent(self, max: int = 10) -> Self:
        return self.order_by("-created_at")[:max]

    def search(self, query: str) -> Self:
        if query:
            query_filter = models.Q()
            for identifier in query.split(","):
                identifier = identifier.strip()
                if identifier.startswith("/") and identifier.endswith("/"):
                    query_filter |= models.Q(
                        order__identifiers__value__iregex=identifier[1:-1]
                    )
                else:
                    query_filter |= models.Q(
                        order__identifiers__value__iexact=identifier.strip()
                    )

            return self.filter(query_filter)

        return self

    def paginated(
        self, curr_page: int | str = 1, per_page: int = 20, order_by="-created_at"
    ) -> tuple[Paginator, Page]:
        return paginate(self.order_by(order_by), curr_page, per_page)


class Certificate(TimestampMixin, Dictable):
    dict_fields = ("id", "repr")
    objects: CertificateQuerySet = CertificateQuerySet.as_manager()
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="certificate"
    )
    metadata = models.JSONField(null=True, encoder=DjangoJSONEncoder)
    chain = models.TextField()

    @property
    def repr(self):
        return f"Certificate <{self.order.name}>"

    def __str__(self):
        return self.order.name

    def save(self, *args, **kwargs):
        self.rebuild_metadata()

        return super().save(*args, **kwargs)

    def rebuild_metadata(self):
        metadata_version = 1
        if not self.metadata or self.metadata.get("version") != metadata_version:
            certs = x509.load_pem_x509_certificates(self.chain.encode())
            # Find the cert that is not a CA
            leaf_cert = None
            for cert in certs:
                try:
                    basic_constraints = cert.extensions.get_extension_for_class(
                        x509.BasicConstraints
                    )
                    if not basic_constraints.value.ca:
                        leaf_cert = cert
                        break
                except cryptography.x509.extensions.ExtensionNotFound:
                    # CAs must have this extension, so this must be the leaf?
                    leaf_cert = cert
                    break

            # Hail mary
            if not leaf_cert:
                # The issued certificate is the last one in the chain
                leaf_cert = certs[-1]

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
