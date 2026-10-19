import inject
import pytest
from acmev2.models import AccountStatus, OrderStatus
from django.contrib.auth.models import Permission
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from certificat.modules.acme import models as db
from certificat.modules.html.nav import Sections
from certificat.modules.perms import Perms
from certificat.settings.dynamic import ApplicationSettings

from ..helpers import create_cert, gen_user


class TestOrders:
    @pytest.fixture(autouse=True)
    def setup_class_members(self, gen_bound_client):
        self.gen_bound_client = gen_bound_client
        client, account, user = self.gen_bound_client()

        self.client = client
        self.acme_user = user
        self.user = user

    def create_order(self, cn="test.localhost", client=None):
        settings = inject.instance(ApplicationSettings)
        settings.finalizer.type = "local"

        return create_cert(client or self.client, cn, [cn])

    @pytest.mark.django_db
    def test_anonymous(self, web_client: Client):
        response = web_client.get(reverse(Sections.Orders.value))
        assert response.status_code == 302

    @pytest.mark.django_db
    def test_logged_in(self, web_client: Client):
        user = gen_user()
        web_client.force_login(user)
        response = web_client.get(reverse(Sections.Orders.value))

        assert response.status_code == 200

    @pytest.mark.django_db
    def test_no_results(self, web_client: Client):
        user = gen_user()
        web_client.force_login(user)
        response = web_client.get(reverse(Sections.Orders.value))

        assert response.status_code == 200
        assert "No accessible orders" in response.text

    @pytest.mark.django_db
    def test_expected_results(self, web_client: Client):
        web_client.force_login(self.user)

        self.create_order("authorized.localhost")
        response = web_client.get(reverse(Sections.Orders.value))

        # pretty fuzzy tests to see if the CNs we should see appear or not
        assert "authorized.localhost" in response.text

        # generate a second account
        new_client, _, new_usr = self.gen_bound_client()
        self.create_order("neworder.localhost", client=new_client)

        response = web_client.get(reverse(Sections.Orders.value))

        # Existing user shouldn't see new order
        assert "neworder.localhost" not in response.text
        assert "authorized.localhost" in response.text

        web_client.force_login(new_usr)
        response = web_client.get(reverse(Sections.Orders.value))

        # New user shouldn't see first order
        assert "neworder.localhost" in response.text
        assert "authorized.localhost" not in response.text

        self.create_order("authorized2.localhost")

        web_client.force_login(self.user)
        response = web_client.get(reverse(Sections.Orders.value))

        # there should now be two orders
        assert "authorized.localhost" in response.text
        assert "authorized2.localhost" in response.text

        # Search for one domain
        response = web_client.get(
            reverse(Sections.Orders.value) + "?filter=authorized.localhost"
        )

        # there should now be one order
        assert "authorized.localhost" in response.text
        assert "authorized2.localhost" not in response.text

    @pytest.mark.django_db
    def test_view_all_orders(self):
        viewer = self.user
        orders = []
        own_orders = []
        for owner in (viewer, gen_user(), gen_user()):
            name = f"account-{owner.pk}"
            binding = db.AccountBinding.generate(owner, name)
            account = db.Account.objects.create(
                name=name,
                status=AccountStatus.valid,
                jwk="{}",
                jwk_thumbprint=name,
            )
            binding.bind_to(account)
            for index in range(2):
                order = db.Order.objects.create(
                    account=account,
                    name=f"order-{owner.pk}-{index}",
                    status=OrderStatus.pending,
                    expires=timezone.now(),
                )
                orders.append(order)
                if owner == viewer:
                    own_orders.append(order)

        for order in orders:
            assert bool(order.accessible_by(viewer)) == (order in own_orders)
        assert set(db.Order.objects.by_user(viewer)) == set(own_orders)

        app_label, codename = Perms.VIEW_ALL_ORDERS.split(".")
        viewer.user_permissions.add(
            Permission.objects.get(content_type__app_label=app_label, codename=codename)
        )
        viewer = type(viewer).objects.get(pk=viewer.pk)

        assert all(order.accessible_by(viewer) for order in orders)
        assert set(db.Order.objects.by_user(viewer)) == set(orders)
