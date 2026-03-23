from dataclasses import dataclass

from certificat.modules.acme import models as db
from certificat.settings.dynamic import ApplicationSettings, EMSignFinalizerSettings
from .api import Client
from .api import (
    generate_order_schema as generate,
    track_order_schema as track,
    get_certificate_schema as cert,
)

from django.utils import timezone
import uuid
from certificat.modules.acme.backends import (
    ErrorResponse,
)
import inject
import logging

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


@dataclass
class GenerateOrderResponse(APIResponse):
    order_number: str = None
    txn: str = None


@dataclass
class TrackOrderResponse(APIResponse):
    order_status: int = 1
    order_status_detail: str = None
    certificate_status: int = 1
    certificate_status_detail: str = None


@dataclass
class GetCertificateResponse(APIResponse):
    rootCertificate: str = None
    caCertificate: str = None
    endEntityCertificate: str = None


class EMSignBackend:
    def generate_order(self, order: db.Order, pem_csr: str) -> GenerateOrderResponse:
        ca_settings: EMSignFinalizerSettings = inject.instance(
            ApplicationSettings
        ).finalizer

        logging.info("EMSign backend received request to generate new order")

        client = Client()
        domain_names = [identifier.value for identifier in order.identifiers.all()]
        order_details = generate.OrderDetails(
            productCode=ca_settings.product_code,
            requestorInformation=generate.RequestorInformation(
                requestorEmail=ca_settings.requestor_email,
                requestorIsdCode=ca_settings.requestor_isd_code,
                requestorMobileNumber=ca_settings.requestor_mobile_number,
                requestorName=ca_settings.requestor_name,
            ),
            organizationDetails=generate.OrganizationDetails(
                prevettingToken=ca_settings.prevetting_token,
                organizationNumber=ca_settings.prevetted_org_number,
            ),
            certificateInformation=generate.CertificateInformation(
                domainName=domain_names[0],
                additionalDomains=domain_names[1:],
            ),
            subscriptionDetails=generate.SubscriptionDetails(),
            csr=pem_csr,
        )
        req = generate.Request(
            meta=generate.Meta(
                accountNumber=ca_settings.account_number,
                authKey=ca_settings.auth_key,
                ts=timezone.now().isoformat(),
                txn=str(uuid.uuid4()),
            ),
            orderDetails=order_details,
        )

        try:
            raw_response = client.generate_order(req)
            response = generate.Response.model_validate(raw_response.json())

            return GenerateOrderResponse(
                raw_response.status_code,
                error=None
                if raw_response.status_code == 200
                else ErrorResponse(response.meta.errorCode, response.meta.errorMessage),
                order_number=response.orderDetails.orderNumber,
                txn=response.meta.txn,
            )
        # Could fail because Pydantic fails to validate the model or a generic requests exception
        except Exception as exc:
            return GenerateOrderResponse(
                500, ErrorResponse("E_GEN", "Generic error: " + str(exc))
            )

    def track_order(self, order_number: str) -> TrackOrderResponse:
        ca_settings: EMSignFinalizerSettings = inject.instance(
            ApplicationSettings
        ).finalizer
        logging.info(
            "EMSign backend received request to track existing order: %s", order_number
        )

        client = Client()
        req = track.Request(
            meta=track.Meta(
                accountNumber=ca_settings.account_number,
                authKey=ca_settings.auth_key,
                ts=timezone.now().isoformat(),
                txn=str(uuid.uuid4()),
            ),
            orderDetails=track.RequestOrderDetails(orderNumber=order_number),
        )

        try:
            raw_response = client.track_order(req)
            response = track.Response.model_validate(raw_response.json())

            return TrackOrderResponse(
                raw_response.status_code,
                error=None
                if raw_response.status_code == 200
                else ErrorResponse(response.meta.errorCode, response.meta.errorMessage),
                order_status=int(response.orderDetails.orderStatusId),
                order_status_detail=response.orderDetails.orderStatus,
                certificate_status=int(response.orderDetails.certificateStatusId),
                certificate_status_detail=response.orderDetails.certificateStatus,
            )
        # Could fail because Pydantic fails to validate the model or a generic requests exception
        except Exception as exc:
            return TrackOrderResponse(
                500, ErrorResponse("E_GEN", "Generic error: " + str(exc))
            )

    def get_certificate(self, order_number: str) -> GetCertificateResponse:
        ca_settings: EMSignFinalizerSettings = inject.instance(
            ApplicationSettings
        ).finalizer
        logging.info(
            "EMSign backend received request to get certificate for order: %s",
            order_number,
        )

        client = Client()
        req = cert.Request(
            meta=cert.Meta(
                accountNumber=ca_settings.account_number,
                authKey=ca_settings.auth_key,
                ts=timezone.now().isoformat(),
                txn=str(uuid.uuid4()),
            ),
            orderDetails=cert.RequestOrderDetails(
                orderNumber=order_number, requestorEmail=ca_settings.requestor_email
            ),
        )

        try:
            raw_response = client.get_certificate(req)
            response = cert.Response.model_validate(raw_response.json())

            return GetCertificateResponse(
                raw_response.status_code,
                error=None
                if raw_response.status_code == 200
                else ErrorResponse(response.meta.errorCode, response.meta.errorMessage),
                rootCertificate=response.certificateDetails.rootCertificate,
                caCertificate=response.certificateDetails.caCertificate,
                endEntityCertificate=response.certificateDetails.endEntityCertificate,
            )
        # Could fail because Pydantic fails to validate the model or a generic requests exception
        except Exception as exc:
            return GetCertificateResponse(
                500, ErrorResponse("E_GEN", "Generic error: " + str(exc))
            )
