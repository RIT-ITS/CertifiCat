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


class ResponseOrderDetails(BaseModel):
    orderStatusId: str
    orderStatus: str
    certificateStatusId: str
    certificateStatus: str


class Response(BaseModel):
    meta: ResponseMeta
    orderDetails: ResponseOrderDetails
