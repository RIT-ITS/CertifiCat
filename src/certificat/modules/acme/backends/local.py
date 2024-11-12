from datetime import datetime, timezone, timedelta
from cryptography.hazmat.primitives import serialization, hashes
from cryptography import x509
from certificat.modules.acme import models as db

from certificat.modules.acme.backends import (
    FinalizeResponse,
    Finalizer,
)
from certificat.settings.dynamic import LocalCASettings


class LocalFinalizer(Finalizer):
    def finalize(self, order: db.Order, pem_csr: str):
        ca_settings = LocalCASettings()

        ca_key = serialization.load_pem_private_key(
            ca_settings.key.encode(), password=None
        )
        ca_cert = x509.load_pem_x509_certificate(ca_settings.cert.encode())
        csr = x509.load_pem_x509_csr(pem_csr.encode())

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
        chain = (
            cert.public_bytes(serialization.Encoding.PEM).decode()
            + ca_cert.public_bytes(serialization.Encoding.PEM).decode()
        )

        db.Certificate.objects.create(order=order, chain=chain)
        return FinalizeResponse(
            bundle=(
                cert.public_bytes(serialization.Encoding.PEM).decode()
                + ca_cert.public_bytes(serialization.Encoding.PEM).decode()
            )
        )
