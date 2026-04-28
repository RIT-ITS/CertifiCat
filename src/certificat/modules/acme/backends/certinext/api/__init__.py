import datetime
import hashlib
import uuid

from . import schema
from certificat.settings.dynamic import ApplicationSettings, CertiNextFinalizerSettings
from certificat.utils import LazyLoggedMethod
import inject
import requests
from . import track_order_schema


import logging

logger = logging.getLogger(__name__)


class CertiNextAPIClient:
    settings: CertiNextFinalizerSettings

    def __init__(self):
        self.settings = inject.instance(ApplicationSettings).finalizer

    def generate_meta(self) -> schema.base.RequestMeta:
        txn = str(uuid.uuid4()).replace("-", "")
        ts = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S%:z"
        )
        hashed_auth_key = hashlib.sha256(
            f"{self.settings.auth_key}{ts}{txn}".encode("utf-8")
        ).hexdigest()

        return schema.base.RequestMeta(
            ts=ts,
            txn=txn,
            accountNumber=self.settings.account_number,
            authKey=hashed_auth_key,
        )

    def generate_order(
        self,
        body: schema.generate_order.Request,
    ) -> requests.Response:
        endpoint = self.settings.api_base + "GenerateOrderSSL"
        logger.debug(
            "CertiNext %s orderDetails=%s",
            endpoint,
            LazyLoggedMethod(
                lambda: body.orderDetails.model_dump_json(indent=4, exclude_unset=True)
            ),
        )

        return requests.post(endpoint, json=body.model_dump(exclude_none=True))

    def track_order(self, body: track_order_schema.Request) -> requests.Response:
        endpoint = self.settings.api_base + "TrackOrder"
        logger.debug(
            "CertiNext %s orderDetails=%s",
            endpoint,
            LazyLoggedMethod(
                lambda: body.orderDetails.model_dump_json(indent=4, exclude_unset=True)
            ),
        )

        return requests.post(endpoint, json=body.model_dump(exclude_none=True))

    def get_certificate(
        self, body: schema.get_certificate.Request
    ) -> requests.Response:
        endpoint = self.settings.api_base + "GetCertificate"
        logger.debug(
            "CertiNext %s orderDetails=%s",
            endpoint,
            LazyLoggedMethod(
                lambda: body.orderDetails.model_dump_json(indent=4, exclude_unset=True)
            ),
        )

        return requests.post(endpoint, json=body.model_dump(exclude_none=True))
