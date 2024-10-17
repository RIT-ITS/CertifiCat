import abc
from dataclasses import dataclass


@dataclass
class ErrorResponse:
    code: int
    description: str


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


class Backend(abc.ABC):
    poll_deadline: int = 360

    @abc.abstractmethod
    def enroll(self, csr: str) -> EnrollResponse:
        pass

    @abc.abstractmethod
    def get(self, ssl_id: str) -> GetResponse:
        pass

    @abc.abstractmethod
    def approve(self, ssl_id: str, message: str):
        pass

    @abc.abstractmethod
    def collect(self, ssl_id: str) -> CollectResponse:
        pass
