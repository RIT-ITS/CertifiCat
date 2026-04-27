from __future__ import annotations

from pydantic import BaseModel
from .base import RequestMeta, ResponseMeta


class RequestorInformation(BaseModel):
    # Name of the requestor
    requestorName: str
    # ISD code of the requestor
    requestorIsdCode: str
    # Mobile number of the requestor
    requestorMobileNumber: str
    # Email of the requestor
    requestorEmail: str
    # Optional requestor designation
    requestorDesignation: str | None = None


class DelegationInformation(BaseModel):
    # Who is the certificate requested for
    contactName: str
    # What is the email of the requestor
    email: str


class OrganizationDetails(BaseModel):
    # Pre-verified domains are used with CertifiCat
    preVetting: str = "1"
    # Existing Org. ID for the associated with the account
    organizationNumber: str
    # Pre-vetting token associated with the organization
    prevettingToken: str


class CertificateInformation(BaseModel):
    # Primary domain name for the server
    domainName: str | None = None
    # Additional domain (SAN) for the server
    additionalDomains: list[str] = []
    # TODO: Come back to this
    autoSecureWWW: str = "1"


class AgreementDetails(BaseModel):
    acceptAgreement: str = "1"
    # Delegated name of the person accepting the agreement
    signerName: str
    # Place of the signer
    signerPlace: str
    # IP address of the signer
    signerIP: str


class SubscriptionDetails(BaseModel):
    # Use default validity period
    # validity: str
    # Decline auto-renew, allow ACME to handle it
    autoRenew: str = "0"


class CustomField(BaseModel):
    fieldID: str
    fieldValue: str


class TechnicalPointOfContact(BaseModel):
    # Name of the technical point of contact
    pocName: str
    # email of the technical point of contact
    pocEmail: str


class AdditionalInformation(BaseModel):
    # Reporting tags used to filter reports
    tags: list[str] | None = []
    # Mandatory only if your administrator requires custom fields
    customFields: list[CustomField] | None = []
    remarks: str
    # Additional email recipients
    recipientEmail: str | None = None
    technicalPointOfContact: TechnicalPointOfContact | None = None


class OrderDetails(BaseModel):
    # Unique product code provided by eMudhra
    productCode: str
    # Accounting model, default is 1 - Cash Model
    accountingModel: str = "1"
    # 1 - Does not submit the order, 0 - Submits the order
    saveAndHold: str = "0"
    # 0 - Re-use consent notification will be sent on order initiation
    # 1 - All order notifications will be sent on order initiation
    emailNotifications: str = "1"
    # Group number for accounting, set to default group number if None
    # groupNumber: str = None
    requestorInformation: RequestorInformation | None = None
    # Optional delegation information
    delegationInformation: DelegationInformation | None = None
    # Optional organization details, required with pre-vetting
    organizationDetails: OrganizationDetails | None = None
    certificateInformation: CertificateInformation
    # Required if prevetting is set to 0, it will always be 1 for CertifiCat
    agreementDetails: AgreementDetails | None = None
    # Auto-renew flags
    subscriptionDetails: SubscriptionDetails
    csr: str
    additionalInformation: AdditionalInformation | None = None
    # Do not generate www variant
    autoSecureWWW: str = "0"


class ResponseOrderDetails(BaseModel):
    # Request ID of the request. May not exist in some cases, unknown
    requestNumber: str = ""
    # ID for the order. May not exist in case of error
    orderNumber: str = ""
    # May not exist in case of error
    trackingURL: str = ""


class Request(BaseModel):
    meta: RequestMeta
    orderDetails: OrderDetails


class Response(BaseModel):
    meta: ResponseMeta
    orderDetails: ResponseOrderDetails | None = None
