import abc
from dataclasses import dataclass
from certificat.modules.acme import models as db


@dataclass
class ErrorResponse:
    code: int
    description: str


@dataclass
class FinalizeResponse:
    error: ErrorResponse = None
    bundle: str = None

    def ok(self) -> bool:
        return self.error is None


class Finalizer(abc.ABC):
    @abc.abstractmethod
    def finalize(self, order: db.Order, pem_csr: str) -> FinalizeResponse:
        pass


class NotReadyException(Exception):
    pass
