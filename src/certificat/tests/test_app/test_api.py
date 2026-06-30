import datetime

from certificat.settings.dynamic import ApplicationSettings
from certificat.modules.acme import models as db
import inject
import pytest
from django.test import Client
from ..helpers import create_cert, gen_user
from django.core.cache import cache
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import Group


class TestApi:
    @pytest.fixture(autouse=True)
    def setup_class_members(self, gen_bound_client):
        self.gen_bound_client = gen_bound_client
        client, account, user = self.gen_bound_client()

        self.client = client
        self.acme_user = user

    def create_order(self):
        settings = inject.instance(ApplicationSettings)
        settings.finalizer.type = "local"

        return create_cert(self.client, "test.localhost", ["test.localhost"])

    @pytest.mark.django_db
    def test_get_cert_activity(self, web_client: Client):
        cache.clear()
        response = web_client.get(reverse("api:cert_activity"))
        assert response.text == "{}"

        self.create_order()
        self.create_order()
        self.create_order()

        first_cert = db.Certificate.objects.first()
        first_cert.created_at = timezone.now() - datetime.timedelta(days=7)
        first_cert.save()

        cache.clear()
        response = web_client.get("/api/cert-activity")
        response_dict = response.json()

        assert len(response_dict.keys()) == 2
        assert sorted(list(response_dict.values())) == [1, 2]

    @pytest.mark.django_db
    def test_edit_binding(self, web_client: Client):
        account_owner = gen_user()
        grp1 = Group.objects.create(name="grp1")
        grp2 = Group.objects.create(name="grp2")
        unprivileged_user = gen_user()

        binding = db.AccountBinding.generate(account_owner, "name", "note")

        response = web_client.get(reverse("api:edit_binding", args=[binding.name]))
        assert response.status_code != 200

        web_client.force_login(unprivileged_user)
        response = web_client.post(reverse("api:edit_binding", args=[binding.id]))
        assert response.status_code == 403

        web_client.force_login(account_owner)

        def _post(mods):
            return web_client.post(
                reverse("api:edit_binding", args=[binding.id]),
                mods,
                content_type="application/json",
            )

        _post({"name": "new-name"})
        binding.refresh_from_db()
        assert binding.name == "new-name"

        _post({"note": "new note"})
        binding.refresh_from_db()
        assert binding.note == "new note"

        _post({"groups": {"add": [grp1.id]}})
        binding.refresh_from_db()
        assert [i.group.id for i in binding.group_scopes.all()] == [grp1.id]

        _post({"groups": {"del": [grp1.id]}})
        binding.refresh_from_db()
        assert len(binding.group_scopes.all()) == 0

        _post({"groups": {"add": [grp1.id, grp2.id]}})
        binding.refresh_from_db()
        assert [i.group.id for i in binding.group_scopes.all()] == [grp1.id, grp2.id]

        _post({"groups": {"del": [grp1.id]}})
        binding.refresh_from_db()
        assert [i.group.id for i in binding.group_scopes.all()] == [grp2.id]

    @pytest.mark.django_db
    def test_edit_preauthorizations(self, web_client: Client):
        account_owner = gen_user()
        superuser = gen_user(is_superuser=True)
        unprivileged_user = gen_user()

        acct = db.Account.objects.create(
            name="test-account",
            jwk="invalid-jwk",
            jwk_thumbprint="invalid-thumbprint",
        )

        response = web_client.get(
            reverse("api:edit_preauthorizations", args=[acct.name])
        )
        assert response.status_code != 200

        # unprivileged users may not edit
        web_client.force_login(unprivileged_user)
        response = web_client.post(
            reverse("api:edit_preauthorizations", args=[acct.name])
        )
        assert response.status_code == 403

        # account owners may not edit
        web_client.force_login(account_owner)
        response = web_client.post(
            reverse("api:edit_preauthorizations", args=[acct.name])
        )
        assert response.status_code == 403

        # only superusers can edit as of right now
        web_client.force_login(superuser)

        def _post(mods):
            return web_client.post(
                reverse("api:edit_preauthorizations", args=[acct.name]),
                mods,
                content_type="application/json",
            )

        # No TLD
        resp = _post({"add": ["invalid"]})
        assert resp.status_code == 400

        # TLD too short
        resp = _post({"add": ["invalid.x"]})
        assert resp.status_code == 400

        # Good addition
        resp = _post({"add": ["valid.tld"]})
        assert acct.preauthorized_identifiers.count() == 1

        # Should create two identifiers
        resp = _post({"add": ["another.valid.tld"]})
        assert acct.preauthorized_identifiers.count() == 2

        # Already added, ignore
        resp = _post({"add": ["valid.tld"]})
        assert acct.preauthorized_identifiers.count() == 2

        # Identifier doesn't exist, not an error
        resp = _post({"del": ["nonexistent.tld"]})
        assert acct.preauthorized_identifiers.count() == 2

        # Good deletion
        resp = _post({"del": ["valid.tld"]})
        assert acct.preauthorized_identifiers.count() == 1

        # Another good deletion, back to 0
        resp = _post({"del": ["another.valid.tld"]})
        assert acct.preauthorized_identifiers.count() == 0

    @pytest.mark.django_db
    def test_get_order_events(self, web_client: Client):
        order = self.create_order()

        web_client.force_login(self.acme_user)
        response = web_client.get(reverse("api:order_events", args=[order.id]))
        assert len(response.json()["events"]) > 0
