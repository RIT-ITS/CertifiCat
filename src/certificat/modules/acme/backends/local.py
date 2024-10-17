from datetime import datetime, timezone, timedelta
from certificat.settings.dynamic import LocalCASettings
import uuid
from cryptography.hazmat.primitives import serialization, hashes
from cryptography import x509

from certificat.modules.acme.backends import (
    ApproveResponse,
    CollectResponse,
    EnrollResponse,
    GetResponse,
    Backend,
)


class LocalBackend(Backend):
    """
    Very simple CA Backend that illustrates how to sign certs with a local keypair.

    The csr -> ssl link is stored in memory, so restarting the service will disrupt any
    in-flight ACME requests.
    """

    csrs = {}

    def __init__(self):
        self.settings = LocalCASettings()

    def enroll(self, csr: str) -> EnrollResponse:
        ssl_id = uuid.uuid4().hex
        self.csrs[ssl_id] = csr

        return EnrollResponse(status=200, ssl_id=ssl_id)

    def get(self, ssl_id: str) -> GetResponse:
        return GetResponse(status=200, cert_status="approved", approved=datetime.now())

    def approve(self, ssl_id: str, message: str):
        return ApproveResponse(status=200)

    def collect(self, ssl_id: str) -> CollectResponse:
        ca_key = serialization.load_pem_private_key(
            self.settings.key.encode(), password=None
        )
        ca_cert = x509.load_pem_x509_certificate(self.settings.cert.encode())
        csr = x509.load_pem_x509_csr(self.csrs[ssl_id].encode())

        builder = (
            x509.CertificateBuilder()
            .subject_name(csr.subject)
            .issuer_name(ca_cert.issuer)
            .public_key(csr.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.now(timezone.utc))
            .not_valid_after(datetime.now(timezone.utc) + timedelta(days=90))
        )

        for ext in csr.extensions:
            builder = builder.add_extension(ext.value, ext.critical)

        cert = builder.sign(ca_key, hashes.SHA256())

        return CollectResponse(
            status=200,
            bundle=cert.public_bytes(serialization.Encoding.PEM).decode()
            + ca_cert.public_bytes(serialization.Encoding.PEM).decode(),
        )
