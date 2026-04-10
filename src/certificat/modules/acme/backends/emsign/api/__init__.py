from certificat.settings.dynamic import ApplicationSettings, EMSignFinalizerSettings
from certificat.utils import LazyLoggedMethod
import inject
import requests
from . import generate_order_schema, track_order_schema, get_certificate_schema


import logging

logger = logging.getLogger(__name__)


class Client:
    settings: EMSignFinalizerSettings

    def __init__(self):
        self.settings = inject.instance(ApplicationSettings).finalizer

    def generate_order(
        self,
        body: generate_order_schema.Request,
    ) -> requests.Response:
        endpoint = self.settings.api_base + "GenerateOrderSSL"
        logger.debug(
            "EMSign %s orderDetails=%s",
            endpoint,
            LazyLoggedMethod(lambda: body.orderDetails.model_dump_json(indent=4)),
        )

        return requests.post(endpoint, json=body.model_dump(exclude_none=True))

    def track_order(self, body: track_order_schema.Request) -> requests.Response:
        endpoint = self.settings.api_base + "TrackOrder"
        logger.debug(
            "EMSign %s orderDetails=%s",
            endpoint,
            LazyLoggedMethod(lambda: body.orderDetails.model_dump_json(indent=4)),
        )

        return requests.post(endpoint, json=body.model_dump(exclude_none=True))

    def get_certificate(
        self, body: get_certificate_schema.Request
    ) -> requests.Response:
        endpoint = self.settings.api_base + "GetCertificate"
        logger.debug(
            "EMSign %s orderDetails=%s",
            endpoint,
            LazyLoggedMethod(lambda: body.orderDetails.model_dump_json(indent=4)),
        )

        return requests.post(endpoint, json=body.model_dump(exclude_none=True))
