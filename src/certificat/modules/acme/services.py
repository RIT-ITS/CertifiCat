import uuid
from certificat.modules.acme.util import gen_id
import inject
from josepy.jwk import JWK
from acmev2.errors import ACMEError
from acmev2.models import (
    AccountResource,
    OrderResource,
    AuthorizationResource,
    ChallengeResource,
    CertResource,
    OrderStatus,
    AuthorizationStatus,
    ChallengeStatus,
)
from acmev2.services import (
    IDirectoryService,
    INonceService,
    IAccountService,
    IOrderService,
    IAuthorizationService,
    IChallengeService,
    ICertService,
    ACMEResourceType,
)
from cryptography.hazmat.primitives import serialization
from certificat.settings.dynamic import ApplicationSettings
import urllib.parse
from django.core.cache import cache
from django.db.models import Subquery
from . import models as db
import json
from certificat.modules import tasks
from django.db import transaction
from django.utils.timezone import make_aware
from django.utils import timezone

AccountIdStr = str
KIDStr = str
HMACStr = str


class DirectoryService(IDirectoryService):
    external_account_required = True
    app_settings = inject.attr(ApplicationSettings)

    def __init__(self):
        self.root_url = urllib.parse.urljoin(self.app_settings.url_root, "/acme")

    def url_base(self) -> str:
        return self.root_url


ONE_HOUR = 60 * 60


class NonceService(INonceService):
    nonce_prefix = "nonce:"

    def generate(self) -> str:
        nonce = uuid.uuid4().hex
        # Some providers will hold onto nonces for a very long time. I'd love to
        # make this shorter, like 60 seconds, but it will fail and certs will
        # not be issued. Hopefully an hour is long enough.
        while not cache.add(f"{self.nonce_prefix}{nonce}", 0, timeout=ONE_HOUR):
            nonce = uuid.uuid4().hex

        return nonce

    def consume(self, nonce: str) -> bool:
        return cache.delete(f"{self.nonce_prefix}{nonce}")


class AccountService(IAccountService):
    def create(self, resource: AccountResource, eab_kid: str = None) -> AccountResource:
        # TODO: Add lock around this to avoid race condition. Will probably never happen
        # except in testing.
        binding: db.AccountBinding | None = None
        if eab_kid:
            binding = db.AccountBinding.objects.get(hmac_id=eab_kid)
            if binding.bound_to is not None:
                raise ACMEError(detail="Attempting to rebind external account")

        account_name = gen_id()
        while db.Account.objects.filter(name=account_name).exists():
            account_name = gen_id()

        account = db.Account.objects.create(
            name=account_name,
            status=resource.status,
            jwk=json.dumps(resource.jwk.to_json()),
            jwk_thumbprint=resource.jwk.thumbprint().hex(),
        )

        db.TaggedEvent.record(db.AccountEventType.BOUND, account)

        if binding:
            binding.bind_to(account)

        resource.id = account.name

        return resource

    def get(self, account_id: str) -> AccountResource | None:
        # the account id is namespaced but we discard the namespace
        # when storing or retrieving.
        account_id = account_id.split("/")[-1]
        try:
            return db.to_pydantic(db.Account.objects.get(name=account_id))
        except db.Account.DoesNotExist:
            return None

    def get_by_jwk(self, jwk: JWK) -> AccountResource | None:
        try:
            return db.to_pydantic(
                db.Account.objects.get(jwk_thumbprint=jwk.thumbprint().hex())
            )
        except db.Account.DoesNotExist:
            return None

    def get_eab_hmac(self, kid: str) -> str | None:
        try:
            return db.AccountBinding.objects.get(hmac_id=kid).hmac_key
        except db.AccountBinding.DoesNotExist:
            return None

    def check_access(
        self, account_id: str, resource_id: str, resource_type: ACMEResourceType
    ) -> bool:
        match resource_type:
            case ACMEResourceType.authz:
                return db.Authorization.objects.filter(
                    name=resource_id, order__account__name=account_id
                ).exists()
            case ACMEResourceType.challenge:
                return db.Challenge.objects.filter(
                    name=resource_id, authorization__order__account__name=account_id
                ).exists()
            case ACMEResourceType.order:
                return db.Order.objects.filter(
                    name=resource_id, account__name=account_id
                ).exists()
            case ACMEResourceType.cert:
                return db.Certificate.objects.filter(
                    order__name=resource_id, order__account__name=account_id
                )


class OrderService(IOrderService):
    def __init__(self):
        pass

    def create(self, resource: OrderResource) -> OrderResource:
        with transaction.atomic():
            order_name = gen_id()
            while db.Order.objects.filter(name=order_name).exists():
                order_name = gen_id()

            order = db.Order.objects.create(
                account_id=Subquery(
                    db.Account.objects.filter(name=resource.account_id).values("id")[:1]
                ),
                name=order_name,
                status=resource.status,
                expires=make_aware(resource.expires),
            )

            db.TaggedEvent.record(db.OrderEventType.CREATED, order)

            # Create identifiers
            for identifier in resource.identifiers:
                identifier_record = db.Identifier.objects.create(
                    order=order, type=identifier.type, value=identifier.value
                )
                identifier.id = identifier_record.id

            resource.id = order.name

            return resource

    def update_status(self, order: OrderResource, new_state: OrderStatus):
        if order.status == new_state:
            return order

        db.Order.objects.filter(name=order.id).update(status=new_state)
        db.TaggedEvent.record_by_type(
            db.OrderEventType.STATUS_UPDATED,
            db.Order,
            order.model_id,
            payload={"from": order.status, "to": new_state},
        )
        order.status = new_state

        return order

    def get(self, order_id: str) -> OrderResource | None:
        try:
            return db.to_pydantic(db.Order.objects.get(name=order_id))
        except db.Order.DoesNotExist:
            return None

    def process_finalization(self, order, csr):
        with transaction.atomic():
            self.update_status(order, OrderStatus.processing)

            db.CertificateRequest.objects.create(
                order_id=Subquery(
                    db.Order.objects.filter(name=order.id).values("id")[:1]
                ),
                csr=csr.public_bytes(encoding=serialization.Encoding.PEM).decode(),
            )
            db.TaggedEvent.record_by_type(
                db.OrderEventType.FINALIZATION_QUEUED, db.Order, order.model_id
            )
            tasks.finalize_order.finalize_order_task(order.id)

        return order


class AuthorizationService(IAuthorizationService):
    def __init__(self):
        self.authorizations = {}

    def create(self, resource: AuthorizationResource) -> AuthorizationResource:
        with transaction.atomic():
            authz_name = gen_id()
            while db.Authorization.objects.filter(name=authz_name).exists():
                authz_name = gen_id()

            authz = db.Authorization.objects.create(
                order_id=Subquery(
                    db.Order.objects.filter(name=resource.order_id).values("id")[:1]
                ),
                identifier_id=resource.identifier.id,
                name=authz_name,
                status=resource.status,
                expires=make_aware(resource.expires),
            )
            db.TaggedEvent.record(db.AuthorizationEventType.CREATED, authz)

            resource.id = authz.name

            return resource

    def update_status(
        self, authz: AuthorizationResource, new_state: AuthorizationStatus
    ):
        if authz.status == new_state:
            return authz

        with transaction.atomic():
            db.Authorization.objects.filter(name=authz.id).update(status=new_state)
            db.TaggedEvent.record_by_type(
                db.AuthorizationEventType.STATUS_UPDATED,
                db.Authorization,
                authz.model_id,
                payload={"from": authz.status, "to": new_state},
            )
            authz.status = new_state

            return authz

    def get(self, authz_id: str) -> AuthorizationResource | None:
        try:
            return db.to_pydantic(db.Authorization.objects.get(name=authz_id))
        except db.Authorization.DoesNotExist:
            return None

    def get_by_order(self, order_id: str) -> list[AuthorizationResource]:
        # TODO: Remove
        pass

    def get_by_chall(self, chall_id: str) -> AuthorizationResource | None:
        # TODO: Remove
        pass


class ChallengeService(IChallengeService):
    def __init__(self):
        pass

    def create(self, resource: ChallengeResource) -> list[ChallengeResource]:
        with transaction.atomic():
            chall_name = gen_id()
            while db.Challenge.objects.filter(name=chall_name).exists():
                chall_name = gen_id()

            chall = db.Challenge.objects.create(
                authorization_id=Subquery(
                    db.Authorization.objects.filter(name=resource.authz_id).values(
                        "id"
                    )[:1]
                ),
                name=chall_name,
                token=resource.token,
                type=resource.type,
                status=resource.status,
            )
            db.TaggedEvent.record(db.ChallengeEventType.CREATED, chall)

            resource.id = chall.name

            return resource

    def update_status(self, chall: ChallengeResource, new_state: ChallengeStatus):
        if chall.status == new_state:
            return chall

        with transaction.atomic():
            updates = {"status": new_state}
            if new_state == ChallengeStatus.valid:
                updates["validated"] = timezone.now()

            db.Challenge.objects.filter(name=chall.id).update(**updates)
            db.TaggedEvent.record(
                db.ChallengeEventType.STATUS_UPDATED,
                db.Challenge.objects.get(name=chall.id),
                payload={"from": chall.status, "to": new_state},
            )
            chall.status = new_state

            return chall

    def get(self, chall_id):
        try:
            return db.to_pydantic(db.Challenge.objects.get(name=chall_id))
        except db.Challenge.DoesNotExist:
            return None

    def queue_validation(self, chall):
        with transaction.atomic():
            self.update_status(chall, ChallengeStatus.processing)
            tasks.validate_challenge.validate_challenge_task(chall.id)
            db.TaggedEvent.record_by_type(
                db.ChallengeEventType.VALIDATION_QUEUED, db.Challenge, chall.model_id
            )

        return chall

    def invalidate(
        self,
        order: OrderResource,
        authz: AuthorizationResource,
        challenge: ChallengeResource,
    ) -> ChallengeResource:
        order_service = inject.instance(IOrderService)
        # The authorization becomes invalid
        self.authz_service.update_status(authz, AuthorizationStatus.invalid)
        self.update_status(challenge, ChallengeStatus.invalid)

        # Get the most up-to-date version of the order
        order = order_service.get(authz.order_id)
        order_service.resolve_state(order)

        return challenge


class CertService(ICertService):
    order_service: OrderService = inject.attr(IOrderService)

    def get(self, ord_id: str) -> CertResource | None:
        try:
            return db.to_pydantic(db.Certificate.objects.get(order__name=ord_id))
        except db.Certificate.DoesNotExist:
            return None
