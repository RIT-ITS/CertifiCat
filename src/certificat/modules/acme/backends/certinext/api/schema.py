from typing import List, Optional

from pydantic import BaseModel


class Requestor(BaseModel):
    name: str
    email: str
    phone: str
    designation: str


class Organization(BaseModel):
    organizationNumber: str
    preVetted: bool = True


class Certificate(BaseModel):
    domain: Optional[str] = None
    additionalDomains: List[str] = []
    # Never making this True
    autoSecureWww: bool = False


class Subscription(BaseModel):
    validityYears: int = 1
    autoRenew: bool = False


class Agreement(BaseModel):
    signerName: str
    signerPlace: str
    accepted: bool = True


class GenerateOrderRequest(BaseModel):
    productVariant: str = "ov"
    # unknown acceptable variants
    emailNotifications: str = "all"
    requestor: Requestor
    organization: Organization
    certificate: Certificate
    subscription: Subscription = Subscription()
    agreement: Agreement
    remarks: str
    csr: str


class GenerateOrderResponse(BaseModel):
    orderId: str
    status: str
    productVariant: str
    domain: str
    createdAt: str
    resolvedProductCode: str
    additionalDomains: List[str] = []


class TrackOrderResponse(BaseModel):
    orderId: str
    status: str


class DownloadCertificateResponse(BaseModel):
    orderId: str
    certificatePem: str
