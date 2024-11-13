from dataclasses import dataclass
import time
import requests

from certificat.modules.acme.backends import (
    ErrorResponse,
    FinalizeResponse,
    Finalizer,
)

from certificat.settings import dynamic
import logging
from certificat.modules.acme import models as db
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class APIResponse:
    status: int
    error: ErrorResponse = None

    def ok(self) -> bool:
        return self.error is None


@dataclass
class EnrollResponse(APIResponse):
    ssl_id: str = None


@dataclass
class GetResponse(APIResponse):
    # Status of the certificate
    cert_status: str = None
    # Approval date
    approved: str = None


@dataclass
class ApproveResponse(APIResponse):
    pass


@dataclass
class CollectResponse(APIResponse):
    bundle: str = None


class SectigoBackend:
    """Organization or department id.
    https://cert-manager.com/api/organization/v1
    """

    org_id: int
    """The certificate profile, like multi-domain, ecv, 90-day expiration etc.
    https://cert-manager.com/api/ssl/v1/types?organizationId=<ORG_ID>
    """
    cert_profile_id: int
    """Customer URI is found in the cert-manager URL. It's probably InCommon or InCommon_test:
    https://cert-manager.com/customer/<CUSTOMER_URI>

    It's passed as the customerUri header.
    """
    customer_uri: str
    """Base URL for the api, all endpoints append to this. In the format:
    https://cert-manager.com/api/ssl/v1/
    """
    api_base: str
    """API username, passed as login header.
    """
    api_user: str
    """API password, passed as password header.
    """
    api_password: str
    """A requests Session, used to provide persistence and a place to hook into the requests."""
    session: requests.Session

    """Approval API username, passed as login header.
    """
    approval_api_user: str
    """Approval API password, passed as password header.
    """
    approval_api_password: str
    """Send emails to this address instead of finding the email from the account. Useful for testing."""
    external_requester_override: str

    """How long the backend should be polled for state transitions."""
    poll_deadline: int

    def __init__(self):
        ca_settings = dynamic.SectigoSettings.get()
        self.api_base = ca_settings.api_base
        self.api_password = ca_settings.api_password
        self.api_user = ca_settings.api_user
        self.approval_api_password = ca_settings.approval_api_password
        self.approval_api_user = ca_settings.approval_api_user
        self.cert_profile_id = ca_settings.cert_profile_id
        self.cert_validity_period = ca_settings.cert_validity_period
        self.customer_uri = ca_settings.customer_uri
        self.external_requester_override = ca_settings.external_requester_override
        self.org_id = ca_settings.org_id
        self.poll_deadline = ca_settings.poll_deadline
        self.session = requests.session()

    def enroll(self, order: db.Order, csr: str) -> EnrollResponse:
        """Enrolls a certificate request.

        Args:
            external_requester (str): Email address of the requester.
            csr (str): A CSR with the -----BEGIN CERTIFICATE REQUEST----- and -----END CERTIFICATE REQUEST----- delimiters included.

        Returns:
            EnrollResponse: The response returned from the api.
        """

        endpoint = "ssl/v1/enroll"
        # External requester is the email of the bound account or a default if no external
        # requester is supplied.
        if self.external_requester_override or not order.account.binding:
            external_requester = self.external_requester_override
        else:
            external_requester = order.account.binding.creator.email

        body = {
            "orgId": self.org_id,
            "certType": self.cert_profile_id,
            "term": self.cert_validity_period,
            "comments": "Submitted through acme-proxy",
            "externalRequester": external_requester,
            "csr": csr,
        }

        response: requests.Response = self.session.post(
            self._build_url(endpoint),
            json=body,
            headers=self._auth_headers(),
        )

        detail = response.json()
        if response.status_code >= 400:
            return EnrollResponse(
                status=response.status_code,
                error=ErrorResponse(
                    code=detail.get("code", -1),
                    description=detail.get("description", "Generic error"),
                ),
            )

        return EnrollResponse(
            status=response.status_code,
            ssl_id=detail.get("sslId"),
            renew_id=detail.get("renewId"),
        )

    def get(self, ssl_id: str) -> GetResponse:
        """Gets the requested certificate's status and approval. Used
        to determine if the cert can be collected or not.

        Args:
            ssl_id (str): SSL id of the certificate.

        Returns:
            GetResponse: Narrow collection of fields on the certificate endpoint.
        """

        endpoint = f"ssl/v1/{ssl_id}"

        response: requests.Response = self.session.get(
            self._build_url(endpoint),
            headers=self._auth_headers(),
        )

        detail = response.json()
        if response.status_code >= 400:
            return GetResponse(
                status=response.status_code,
                error=ErrorResponse(
                    code=detail.get("code", -1),
                    description=detail.get(
                        "description", "Generic error getting certificate."
                    ),
                ),
            )

        return GetResponse(
            status=response.status_code,
            cert_status=detail.get("status", "unknown").lower(),
            approved=detail.get("approved"),
        )

    def approve(self, ssl_id: str, message: str) -> ApproveResponse:
        endpoint = f"ssl/v1/approve/{ssl_id}"

        body = {"message": message}

        response: requests.Response = self.session.post(
            self._build_url(endpoint),
            json=body,
            headers=self._auth_headers(profile="approval"),
        )

        if response.status_code >= 400:
            detail = response.json()
            return ApproveResponse(
                status=response.status_code,
                error=ErrorResponse(
                    code=detail.get("code", -1),
                    description=detail.get(
                        "description", "Generic error approving certificate."
                    ),
                ),
            )

        return ApproveResponse(status=response.status_code)

    def collect(self, ssl_id: str) -> CollectResponse:
        """Polls the collect endpoint and returns the bundle when complete.

        Args:
            ssl_id (str): Certificate unique identifier

        Returns:
            CollectResponse: The response returned from the api
        """

        endpoint = f"ssl/v1/collect/{ssl_id}?format=x509"
        response: requests.Response = self.session.get(
            self._build_url(endpoint),
            headers=self._auth_headers(),
        )

        if response.status_code == 200:
            return CollectResponse(status=response.status_code, bundle=response.text)
        else:
            return CollectResponse(
                status=response.status_code,
                error=ErrorResponse(code=101, description=response.text),
            )

    def _auth_headers(self, profile: str = None) -> dict[str, str]:
        if not profile:
            return {
                "login": self.api_user,
                "password": self.api_password,
                "customerUri": self.customer_uri,
            }
        if profile == "approval":
            return {
                "login": self.approval_api_user,
                "password": self.approval_api_password,
                "customerUri": self.customer_uri,
            }

    def _build_url(self, endpoint: str) -> str:
        full_url = self.api_base
        if not self.api_base.endswith("/"):
            full_url += "/"

        return f"{full_url}{endpoint}"


class SectigoFinalizer(Finalizer):
    backend: SectigoBackend = None

    def __init__(self):
        self.backend = SectigoBackend()

    def finalize(self, order: db.Order, pem_csr):
        log_prefix = "order " + order.name

        processing_state: db.SectigoOrderProcessingState = (
            db.SectigoOrderProcessingState.for_order(order)
        )

        if processing_state.state == db.SectigoOrderProcessingState.Choices.SUBMITTED:
            logger.info(f"{log_prefix}: enrolling csr")
            # Enroll the certificate. This kicks off a process and the CA has to issue a new certificate
            # and either auto-approve it or ask the user to approve it.

            enroll_response = self.backend.enroll(order, pem_csr)
            processing_state.ssl_id = enroll_response.ssl_id
            processing_state.save()

            if not enroll_response.ok():
                raise Exception(
                    f"Error {enroll_response.error.code}: {enroll_response.error.description}"
                )

            processing_state.transition_to(
                db.SectigoOrderProcessingState.Choices.ENROLLED
            )

        if processing_state.state == db.SectigoOrderProcessingState.Choices.ENROLLED:
            ready_for_approval = False
            approved = False
            # Poll the certificate endpoint every few seconds to see if it's ready for approval. It may also
            # be auto-approved depending on the rules set up for the org/department.
            start = datetime.now()
            while not (ready_for_approval or approved):
                logger.info(f"{log_prefix}: polling for approval")
                get_response = self.backend.get(processing_state.ssl_id)
                if not get_response.ok():
                    raise Exception(
                        f"Error {get_response.error.code}: {get_response.error.description}"
                    )

                ready_for_approval = get_response.cert_status == "requested"
                approved = get_response.approved is not None

                if (datetime.now() - start).seconds > self.backend.poll_deadline:
                    raise Exception(
                        "Polling deadline exceeded for state " + processing_state.state
                    )

                if not (ready_for_approval or approved):
                    time.sleep(1)

            # If the certificate isn't approved we need to make a final call to approve it.
            if not approved:
                logger.info(f"{log_prefix}: approving certificate")
                approve_response = self.backend.approve(
                    processing_state.ssl_id, message="Auto-approved by ACME"
                )
                if not approve_response.ok():
                    raise Exception(
                        f"Error {approve_response.error.code}: {approve_response.error.description}"
                    )

                approved = True

            processing_state.transition_to(
                db.SectigoOrderProcessingState.Choices.APPROVED
            )

        if processing_state.state == db.SectigoOrderProcessingState.Choices.APPROVED:
            logger.info("collecting certificate")
            # Get the certificate PEM bundle

            collect_response = self.backend.collect(processing_state.ssl_id)
            if not collect_response.ok():
                raise Exception(
                    f"Error {collect_response.error.code}: {collect_response.error.description}"
                )

            # Some clients (like certbot) expect the bundle to end with a newline and will
            # fail if it doesn't.
            if not collect_response.bundle.endswith("\n"):
                collect_response.bundle += "\n"

            db.Certificate.objects.create(order=order, chain=collect_response.bundle)
            processing_state.transition_to(
                db.SectigoOrderProcessingState.Choices.COLLECTED
            )

        if processing_state.state == db.SectigoOrderProcessingState.Choices.COLLECTED:
            return FinalizeResponse(
                bundle=db.Certificate.objects.get(order=order).chain
            )
