import datetime
import hashlib
import logging
import uuid
from typing import Optional
from urllib.parse import urljoin

import inject
import requests

from certificat.settings.dynamic import ApplicationSettings, CertiNextFinalizerSettings
from certificat.utils import LazyLoggedMethod

from . import schema

logger = logging.getLogger(__name__)


class CertiNextAPIError(Exception):
    pass


class CertiNextAPIClient:
    settings: CertiNextFinalizerSettings
    access_token: Optional[str] = None

    def __init__(self):
        self.settings = inject.instance(ApplicationSettings).finalizer

    def ensure_access_token(self) -> str:
        if self.access_token:
            return self.access_token

        params = {
            "grant_type": "client_credentials",
            "client_id": self.settings.oauth_client_id,
            "client_secret": self.settings.oauth_client_secret,
        }

        endpoint = urljoin(self.settings.api_base, "oauth/token")
        logger.debug(
            "CertiNext request: %s client_id=%s",
            endpoint,
            self.settings.oauth_client_id,
        )
        resp: requests.Response = requests.post(
            endpoint,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=params,
            timeout=5,
        )
        # Access token errors have different shape from other endpoints
        if resp.status_code != 200:
            try:
                body = resp.json()
                exception_message = f"{body['error']}: {body['error_description']}"
            except:  # noqa: E722
                exception_message = "Generic error getting OAuth access token"

            raise CertiNextAPIError(exception_message)

        self.access_token = resp.json()["access_token"]
        return self.access_token

    def generate_order(
        self,
        body: schema.GenerateOrderRequest,
    ) -> schema.GenerateOrderResponse:
        endpoint = urljoin(self.settings.api_base, "api/certinext/v2/ssl-certificates")
        logger.debug(
            "CertiNext request: %s orderRequest=%s",
            endpoint,
            LazyLoggedMethod(
                lambda: body.model_dump_json(indent=4, exclude_unset=True)
            ),
        )

        headers = {
            "Authorization": f"Bearer {self.ensure_access_token()}",
            "X-Product-Code": self.settings.product_code,
            "Idempotency-Key": uuid.uuid4().hex,
        }

        resp: requests.Response = requests.post(
            endpoint,
            headers=headers,
            json=body.model_dump(exclude_none=True),
            timeout=10,
        )
        logger.debug("CertiNext response: %s", resp.text)

        if resp.status_code != 200:
            try:
                body = resp.json()
                exception_message = f"{body['title']}: {body['detail']} ({body.get('errors', 'No extra detail included')})"
            except:  # noqa: E722
                exception_message = (
                    f"HTTP_{resp.status_code} error generating the order"
                )

            raise CertiNextAPIError(exception_message)

        return schema.GenerateOrderResponse.model_validate(resp.json())

    def track_order(self, order_id: str) -> schema.TrackOrderResponse:
        endpoint = urljoin(
            self.settings.api_base, f"api/certinext/v2/ssl-certificates/{order_id}"
        )
        logger.debug("CertiNext request: %s orderId=%s", endpoint, order_id)
        headers = {
            "Authorization": f"Bearer {self.ensure_access_token()}",
        }
        resp: requests.Response = requests.get(endpoint, headers=headers)
        logger.debug("CertiNext response: %s", resp.text)

        if resp.status_code != 200:
            try:
                body = resp.json()
                exception_message = f"{body['title']}: {body['detail']}"
            except:  # noqa: E722
                exception_message = f"HTTP_{resp.status_code} error tracking the order"

            raise CertiNextAPIError(exception_message)

        return schema.TrackOrderResponse.model_validate(resp.json())

    def download_certificate(self, order_id: str) -> schema.DownloadCertificateResponse:
        endpoint = urljoin(
            self.settings.api_base,
            f"api/certinext/v2/ssl-certificates/{order_id}/certificate",
        )
        logger.debug("CertiNext request: %s orderId=%s", endpoint, order_id)
        headers = {
            "Authorization": f"Bearer {self.ensure_access_token()}",
            "Accept": "application/x-pem-file",
        }
        resp: requests.Response = requests.get(endpoint, headers=headers)
        logger.debug("CertiNext response: %s", resp.text)

        if resp.status_code != 200:
            try:
                body = resp.json()
                exception_message = f"{body['title']}: {body['detail']}"
            except:  # noqa: E722
                exception_message = (
                    f"HTTP_{resp.status_code} error downloading the certificate"
                )

            raise CertiNextAPIError(exception_message)

        return schema.DownloadCertificateResponse(
            orderId=order_id, certificatePem=resp.text
        )
