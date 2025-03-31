#!/usr/bin/env python

"""
Before using this, you have to change the config.yml to make the url_root parameter
agree with the seed.py domain. Likely you will have to change it to http://certificat.localtest.me

If you don't, you will get unauthorized errors
"""

import datetime
from certificat.settings.dynamic import ApplicationSettings
from certificat.tests.conftest import LocalACMEAdapter
import inject
import acme.client
from certificat.tests import helpers
from certificat.modules.acme import models as db
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import josepy
from acmev2.services import (
    IDirectoryService,
    IChallengeService,
    IOrderService,
    IAuthorizationService,
)
from acmev2.models import ChallengeStatus, AuthorizationStatus
from faker import Faker

fake = Faker()


def new_bound_client(
    root_url: str,
    user_kwargs: dict = {},
    binding_note: str = "",
    binding_name: str = "",
):
    user = helpers.gen_user(**user_kwargs)
    binding = db.AccountBinding.generate(user, name=binding_name, note=binding_note)

    rsa_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    account_key = josepy.JWKRSA(key=rsa_key)

    net = acme.client.ClientNetwork(account_key, user_agent="certificat.tests")
    net.session.mount(f"{root_url}/acme/", LocalACMEAdapter())
    directory_service = inject.instance(IDirectoryService)

    acme_client = acme.client.ClientV2(
        acme.client.messages.Directory.from_json(directory_service.get_directory()),
        net=net,
    )

    account_public_key = acme_client.net.key.public_key()
    eab = acme.client.messages.ExternalAccountBinding.from_data(
        account_public_key=account_public_key,
        kid=binding.hmac_id,
        hmac_key=binding.hmac_key,
        directory=acme_client.directory,
    )

    registration = acme.client.messages.NewRegistration.from_data(
        email="email@acme.edu" if not user else user.email,
        terms_of_service_agreed=True,
        external_account_binding=eab,
    )

    return acme_client.new_account(registration), acme_client, binding, user


def new_order(cn: str, sans: list[str], client: acme.client.ClientV2):
    csr = helpers.gen_csr(
        cn=cn or "acme.localhost",
        sans=sans or ["acme.localhost", "acme2.localhost"],
    )
    new_order = client.new_order(csr.public_bytes(serialization.Encoding.PEM))
    return new_order, csr


def create_cert(client: acme.client.ClientV2, cn: str, sans: list[str]):
    settings = inject.instance(ApplicationSettings)
    settings.finalizer_module = "certificat.modules.acme.backends.local.LocalFinalizer"

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
    order_service.resolve_state(order_service.get(ord_id))
    finalization = client.finalize_order(
        order, datetime.datetime.now() + datetime.timedelta(seconds=5)
    )


def run():
    for i in range(150):
        print(i)
        first_name = fake.first_name()
        last_name = fake.last_name()
        username = fake.user_name() + str(i)
        email = fake.email(domain="acme.edu")
        registration, client, binding, user = new_bound_client(
            "http://certificat.localtest.me",
            user_kwargs={
                "username": username,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
            },
            binding_name=fake.sentence(4)[:-1],
            binding_note=fake.paragraph(),
        )

        for _ in range(fake.random_digit_above_two()):
            cn = fake.word() + ".acme.edu"
            sans = [cn]
            for i in range(fake.random_digit_above_two()):
                sans.append(fake.word() + ".acme.edu")

        create_cert(client, cn, sans)

    print("randomizing dates")
    for cert in db.Certificate.objects.all():
        start = fake.date_between(
            datetime.datetime.now() - datetime.timedelta(days=370)
        )
        cert.created_at = start
        cert.save()

        cert.order.created_at = start
        cert.order.save()

        cert.order.account.created_at = start
        cert.order.account.save()

        cert.order.account.binding.created_at = start
        cert.order.account.binding.save()


run()

# models.User.objects.exclude(username='admin').delete()
# db.Account.objects.filter(binding=None)
