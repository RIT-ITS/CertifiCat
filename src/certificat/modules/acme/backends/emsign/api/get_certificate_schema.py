from __future__ import annotations

from pydantic import BaseModel


class Meta(BaseModel):
    ver: str = "1.0"
    ts: str
    txn: str
    accountNumber: str
    authKey: str


class RequestOrderDetails(BaseModel):
    orderNumber: str
    requestorEmail: str


class Request(BaseModel):
    meta: Meta
    orderDetails: RequestOrderDetails


class ResponseMeta(BaseModel):
    ver: str
    ts: str
    txn: str
    status: str
    errorCode: str
    errorMessage: str


class ResponseCertDetails(BaseModel):
    rootCertificate: str
    caCertificate: str
    endEntityCertificate: str
    # TODO: When is this populated?
    subCACertificate: str = None


class Response(BaseModel):
    meta: ResponseMeta
    certificateDetails: ResponseCertDetails
