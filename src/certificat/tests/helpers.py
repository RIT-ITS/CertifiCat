from django.contrib.auth.models import User
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from contextlib import contextmanager
import datetime
from acme import messages, challenges, standalone, client
import acme.client
import acme.messages
from cryptography.hazmat.primitives import serialization
import inject
from acmev2.services import (
    IChallengeService,
    IOrderService,
    IAuthorizationService,
)
from acmev2.models import ChallengeStatus, AuthorizationStatus


class HelperGlobals:
    usr_cnt = 0


_glob = HelperGlobals()


def gen_user(**kwargs):
    _glob.usr_cnt += 1
    defaults = {
        "username": f"usr{_glob.usr_cnt}",
        "email": f"usr{_glob.usr_cnt}@acme.edu",
        "password": "passw0rd",
    }
    return User.objects.create_user(**(defaults | kwargs))


def gen_csr(
    key: rsa.RSAPrivateKey = None,
    cn: str = "acme.localhost",
    sans: list[str] = ["acme.localhost", "acme2.localhost"],
) -> x509.CertificateSigningRequest:
    builder = x509.CertificateSigningRequestBuilder().subject_name(
        x509.Name(
            [
                x509.NameAttribute(NameOID.COMMON_NAME, cn),
            ]
        )
    )

    if not key:
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    if sans:
        builder = builder.add_extension(
            x509.SubjectAlternativeName(
                [
                    # Describe what sites we want this certificate for.
                    x509.DNSName(n)
                    for n in sans
                ]
            ),
            critical=False,
            # Sign the CSR with our private key.
        )
    csr = builder.sign(key, hashes.SHA256())

    return csr


@contextmanager
def challenge_server(http_01_resources, port=80):
    """Manage standalone server set up and shutdown."""

    # Setting up a fake server that binds at PORT and any address.
    address = ("", port)
    try:
        servers = standalone.HTTP01DualNetworkedServers(address, http_01_resources)
        # Start client standalone web server.
        servers.serve_forever()
        yield servers
    finally:
        # Shutdown client web server and unbind from PORT
        servers.shutdown_and_server_close()


def select_failed_authorizations(order: acme.client.messages.OrderResource):
    failed_auth = [
        a.body.identifier.value
        for a in order.authorizations
        if a.body.status.name != "valid"
    ]
    return failed_auth


def do_challenge(
    acme_client: acme.client.ClientV2,
    order: acme.messages.OrderResource,
):
    http_challenges = select_http01_challenges(order)
    # will set up a local server answering at http://localhost/.well-known/acme-challenge/<TOKEN>
    order = perform_http01(acme_client, http_challenges, order)
    return order


def perform_http01(
    client_acme: client.ClientV2, challenges, orderr
) -> messages.OrderResource:
    """Set up standalone webserver and perform HTTP-01 challenge."""
    resources = []
    for chall in challenges:
        response, validation = chall.response_and_validation(client_acme.net.key)

        resource = standalone.HTTP01RequestHandler.HTTP01Resource(
            chall=chall.chall, response=response, validation=validation
        )
        resources.append(resource)

    with challenge_server(set(resources)):
        for chall in challenges:
            # Let the CA server know that we are ready for the challenge.
            client_acme.answer_challenge(chall, response)

        # Wait for challenge status and then issue a certificate.
        # It is possible to set a deadline time.
        deadline = datetime.datetime.now() + datetime.timedelta(seconds=5)
        return client_acme.poll_authorizations(orderr, deadline)


def new_order(cn: str, sans: list[str], client: acme.client.ClientV2):
    csr = gen_csr(
        cn=cn or "acme.localhost",
        sans=sans or ["acme.localhost", "acme2.localhost"],
    )
    new_order = client.new_order(csr.public_bytes(serialization.Encoding.PEM))
    return new_order, csr


def create_cert(client: acme.client.ClientV2, cn: str, sans: list[str]):
    order, csr = new_order(cn=cn, sans=sans, client=client)
    ord_id = order.uri.split("/")[-1]
    chall_service = inject.instance(IChallengeService)
    auth_service = inject.instance(IAuthorizationService)
    for auth in order.authorizations:
        auth_id = auth.uri.split("/")[-1]
        auth_service.update_status(auth_service.get(auth_id), AuthorizationStatus.valid)
        chall_id = auth.body.challenges[0].uri.split("/")[-1]
        chall_service.update_status(chall_service.get(chall_id), ChallengeStatus.valid)

    order_service = inject.instance(IOrderService)
    order_resource = order_service.get(ord_id)
    order_service.process_finalization(order_resource, csr)
    order_service.resolve_state(order_resource)

    return order_resource


def poll_finalizations(client_acme: client.ClientV2, orderr, timeout=5):
    deadline = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
    return client_acme.poll_finalization(orderr, deadline)


def finalize_order(client_acme: client.ClientV2, orderr, timeout=5):
    deadline = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
    return client_acme.finalize_order(orderr, deadline)


def select_http01_challenges(order: messages.OrderResource):
    """Extract authorization resource from within order resource."""
    # Authorization Resource: authz.
    # This object holds the offered challenges by the server and their status.
    authz_list = order.authorizations
    http_challenges = []
    for authz in authz_list:
        # Choosing challenge.
        # authz.body.challenges is a set of ChallengeBody objects.
        for i in authz.body.challenges:
            # Find the supported challenge.
            if isinstance(i.chall, challenges.HTTP01):
                http_challenges.append(i)

    return http_challenges
