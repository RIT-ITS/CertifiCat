from dataclasses import dataclass
from typing import Generic, TypeVar

from certificat.modules.acme import models as db
from .api import CertiNextAPIError, schema
from certificat.settings.dynamic import ApplicationSettings, CertiNextFinalizerSettings
from .api import CertiNextAPIClient

from certificat.modules.acme.backends import (
    ErrorResponse,
)
import inject
import logging
from cryptography import x509
from cryptography.x509.oid import NameOID

logger = logging.getLogger(__name__)


@dataclass
class APIResponse:
    status: int
    error: ErrorResponse = None

    def ok(self) -> bool:
        return self.error is None

    def raise_if_not_ok(self):
        if not self.ok():
            code = self.error.code if self.error.code else f"HTTP_{self.status}"
            description = (
                self.error.description
                if self.error.description
                else "No description given"
            )

            raise Exception(f"Error {code}: {description}")


T = TypeVar("T")


@dataclass
class BackendError:
    description: str


@dataclass
class GenerateOrderResponse:
    order_number: str
    status: str


@dataclass
class TrackOrderResponse:
    status: str


@dataclass
class CertificateResponse:
    cert: str


class BackendResponse(Generic[T]):
    def __init__(self, wrapped: T | BackendError):
        self.wrapped = wrapped

    @property
    def error(self):
        match self.wrapped:
            case BackendError():
                return self.wrapped

        return None

    def is_error(self):
        match self.wrapped:
            case BackendError():
                return True
            case _:
                return False


class CertiNextBackend:
    def generate_order(
        self, order: db.Order, pem_csr: str
    ) -> BackendResponse[GenerateOrderResponse]:
        ca_settings: CertiNextFinalizerSettings = inject.instance(
            ApplicationSettings
        ).finalizer

        csr = x509.load_pem_x509_csr(pem_csr.encode())
        try:
            san_extension = csr.extensions.get_extension_for_class(
                x509.SubjectAlternativeName
            )
            sans = san_extension.value.get_values_for_type(x509.DNSName)
        except x509.extensions.ExtensionNotFound:
            sans = []

        try:
            cn = csr.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        except:  # noqa: E722
            cn = sans[0]

        logging.info("CertiNext backend received request to generate new order")

        client = CertiNextAPIClient()
        cert_info = schema.Certificate()
        if cn:
            cert_info.domain = cn

        if sans:
            cert_info.additionalDomains = sans

        order_request = schema.GenerateOrderRequest(
            agreement=schema.Agreement(
                signerName=ca_settings.agreement_signer,
                signerPlace=ca_settings.agreement_signer_place,
            ),
            certificate=cert_info,
            csr=pem_csr,
            organization=schema.Organization(organizationNumber=ca_settings.org_number),
            productVariant=ca_settings.product_variant,
            remarks=ca_settings.order_remarks,
            requestor=schema.Requestor(
                designation=ca_settings.requestor_designation,
                email=ca_settings.requestor_email,
                name=ca_settings.requestor_name,
                phone=ca_settings.requestor_phone,
            ),
        )

        try:
            response = client.generate_order(order_request)
            return BackendResponse(
                GenerateOrderResponse(
                    order_number=response.orderId, status=response.status
                )
            )
        except CertiNextAPIError as exc:
            return BackendResponse(BackendError(str(exc)))
        # Could fail because Pydantic fails to validate the model or a generic requests exception
        except Exception as exc:
            return BackendResponse(BackendError("Generic error: " + str(exc)))

    def track_order(self, order_id: str) -> BackendResponse[TrackOrderResponse]:
        try:
            client = CertiNextAPIClient()
            response = client.track_order(order_id)
            return BackendResponse(TrackOrderResponse(status=response.status))
        except CertiNextAPIError as exc:
            return BackendResponse(BackendError(str(exc)))
        # Could fail because Pydantic fails to validate the model or a generic requests exception
        except Exception as exc:
            return BackendResponse(BackendError("Generic error: " + str(exc)))

    def get_certificate(self, order_id: str) -> BackendResponse[CertificateResponse]:
        try:
            client = CertiNextAPIClient()
            response = client.download_certificate(order_id)
            return BackendResponse(CertificateResponse(cert=response.certificatePem))
        except CertiNextAPIError as exc:
            return BackendResponse(BackendError(str(exc)))
        # Could fail because Pydantic fails to validate the model or a generic requests exception
        except Exception as exc:
            return BackendResponse(BackendError("Generic error: " + str(exc)))
