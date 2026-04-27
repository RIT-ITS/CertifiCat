from __future__ import annotations

from pydantic import BaseModel
from .base import RequestMeta, ResponseMeta


class RequestOrderDetails(BaseModel):
    orderNumber: str
    requestorEmail: str


class ResponseCertDetails(BaseModel):
    rootCertificate: str
    caCertificate: str
    endEntityCertificate: str
    # TODO: When is this populated?
    subCACertificate: str = None


class Request(BaseModel):
    meta: RequestMeta
    orderDetails: RequestOrderDetails


class Response(BaseModel):
    meta: ResponseMeta
    certificateDetails: ResponseCertDetails | None = None
