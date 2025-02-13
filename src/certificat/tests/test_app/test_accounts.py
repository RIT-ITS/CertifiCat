    import pytest
    from certificat.modules.html.nav import Sections
    from django.urls import reverse
    from django.test import Client
    from ..helpers import gen_user
    from certificat.modules.acme import models as db
    from acmev2.models import AccountStatus
    from django.contrib.auth.models import Group


    @pytest.mark.django_db
    def test_anonymous(web_client: Client):
        response = web_client.get(reverse(Sections.Accounts.value))
        assert response.status_code == 302


    @pytest.mark.django_db
    def test_logged_in(web_client: Client):
        user = gen_user()
        web_client.force_login(user)
        response = web_client.get(reverse(Sections.Accounts.value))

        assert response.status_code == 200


    @pytest.mark.django_db
    def test_add_binding(authenticated_web_client: Client):
        name = "account name"
        note = "account note"
        response = authenticated_web_client.post(
            reverse(Sections.Accounts.value), {"scope": 1, "name": name, "note": note}
        )

        assert response.status_code == 302
        binding = db.AccountBinding.objects.order_by("-created_at").first()
        assert binding.name == name
        assert binding.note == note


    @pytest.mark.django_db
    def test_binding_setup(authenticated_web_client: Client):
        # make sure activation shows without error, ensure the activation
        # template is used

        binding = db.AccountBinding.generate(
            authenticated_web_client.test_user, "name", "note"
        )

        response = authenticated_web_client.get(reverse("account", args=[binding.id]))
        assert response.status_code == 200
        assert "certificat/account.activate.html" in [t.name for t in response.templates]


    @pytest.mark.django_db
    def test_delete_unbound_binding(authenticated_web_client: Client):
        binding = db.AccountBinding.generate(
            authenticated_web_client.test_user, "name", "note"
        )

        response = authenticated_web_client.post(
            reverse("account", args=[binding.id]), {"delete-binding": "1"}
        )
        assert response.status_code == 302
        assert not db.AccountBinding.objects.filter(id=binding.id).exists()


    @pytest.mark.django_db
    def test_bound_account(authenticated_web_client: Client, acme_newacct):
        binding = db.AccountBinding.generate(
            authenticated_web_client.test_user, "name", "note"
        )
        acme_newacct(with_eab=True, binding=binding, user=binding.creator)
        response = authenticated_web_client.get(reverse("account", args=[binding.id]))

        assert response.status_code == 200
        assert "certificat/account.html" in [t.name for t in response.templates]


    @pytest.mark.django_db
    def test_disable_account(authenticated_web_client: Client, acme_newacct):
        binding = db.AccountBinding.generate(
            authenticated_web_client.test_user, "name", "note"
        )
        acme_newacct(with_eab=True, binding=binding, user=binding.creator)

        binding.refresh_from_db()
        assert binding.bound_to.status == AccountStatus.valid

        response = authenticated_web_client.post(
            reverse("account", args=[binding.id]), {"revoke-account": "1"}
        )

        assert response.status_code == 302
        binding.refresh_from_db()
        assert binding.bound_to.status == AccountStatus.revoked


    @pytest.mark.django_db
    def test_stop_delete_bound_account(authenticated_web_client: Client, acme_newacct):
        binding = db.AccountBinding.generate(
            authenticated_web_client.test_user, "name", "note"
        )
        acme_newacct(with_eab=True, binding=binding, user=binding.creator)

        binding.refresh_from_db()
        assert binding.bound_to.status == AccountStatus.valid

        response = authenticated_web_client.post(
            reverse("account", args=[binding.id]), {"delete-binding": "1"}
        )

        assert response.status_code == 302
        assert db.AccountBinding.objects.filter(id=binding.id).exists()


    @pytest.mark.django_db
    def test_account_sharing(authenticated_web_client: Client, acme_newacct):
        account_owner = gen_user()
        binding = db.AccountBinding.generate(account_owner, "name", "note")

        acme_newacct(with_eab=True, binding=binding, user=account_owner)
        response = authenticated_web_client.get(reverse("account", args=[binding.id]))

        assert response.status_code == 403

        group = Group.objects.create(name="acme")
        account_owner.groups.add(group)
        authenticated_web_client.test_user.groups.add(group)
        db.AccountBindingGroupScope.objects.create(binding=binding, group=group)

        response = authenticated_web_client.get(reverse("account", args=[binding.id]))
        assert response.status_code == 200
