from __future__ import annotations

from pydantic import BaseModel
from .schema.base import RequestMeta, ResponseMeta


class RequestOrderDetails(BaseModel):
    orderNumber: str


class Request(BaseModel):
    meta: RequestMeta
    orderDetails: RequestOrderDetails


class ResponseOrderDetails(BaseModel):
    orderStatusId: str
    orderStatus: str
    certificateStatusId: str
    certificateStatus: str


class Response(BaseModel):
    meta: ResponseMeta
    orderDetails: ResponseOrderDetails
