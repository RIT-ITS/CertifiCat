import inject
import pytest
from acmev2.models import AccountStatus
from django.contrib.auth.models import Group, Permission
from django.test import Client
from django.urls import reverse

from certificat.modules.acme import models as db
from certificat.modules.html.nav import Sections
from certificat.modules.perms import Perms
from certificat.modules.tasks.finalize_order import get_finalizer
from certificat.settings.dynamic import (
    ACMEFinalizerSettings,
    AlternativeFinalizerSettings,
    ApplicationSettings,
)

from ..helpers import gen_user


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


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("role", "expected_status"),
    [
        ("owner", 200),
        ("account_admin", 200),
        ("superuser", 200),
        ("creator", 403),
        ("group_member", 403),
        ("viewer", 403),
        ("unrelated", 403),
    ],
)
def test_transfer_ownership_permission(web_client: Client, role, expected_status):
    creator = gen_user()
    owner = gen_user()
    new_owner = gen_user()
    binding = db.AccountBinding.objects.create(
        creator=creator,
        owner=owner,
        name="account to transfer",
        hmac_id="transfer-permission-test",
        hmac_key="transfer-permission-test-key",
    )

    if role == "owner":
        user = owner
    elif role == "creator":
        user = creator
    else:
        user = gen_user(is_superuser=role == "superuser")

    if role == "group_member":
        group = Group.objects.create(name="shared-account")
        user.groups.add(group)
        db.AccountBindingGroupScope.objects.create(binding=binding, group=group)
        # Group members can edit the account, but cannot transfer ownership.
        assert binding.editable_by(user)
    elif role in ("viewer", "account_admin"):
        permission = (
            Perms.VIEW_ALL_ACCOUNTS
            if role == "viewer"
            else Perms.CHANGE_ALL_ACCOUNTS
        )
        app_label, codename = permission.split(".")
        user.user_permissions.add(
            Permission.objects.get(content_type__app_label=app_label, codename=codename)
        )

    web_client.force_login(user)
    response = web_client.post(
        reverse("api:edit_binding", args=[binding.id]),
        {"owner": new_owner.username},
        content_type="application/json",
    )

    assert response.status_code == expected_status
    binding.refresh_from_db()
    assert binding.owner == (new_owner if expected_status == 200 else owner)
    assert binding.creator == creator


@pytest.mark.django_db
def test_finalizer_selection(authenticated_web_client: Client, acme_newacct):
    binding = db.AccountBinding.generate(
        authenticated_web_client.test_user, "name", "note"
    )
    acme_newacct(with_eab=True, binding=binding, user=binding.creator)

    binding.refresh_from_db()
    assert binding.bound_to
    account = binding.bound_to

    settings = inject.instance(ApplicationSettings)

    def assert_path_is(obj: any, path: str):
        assert f"{obj.__module__}.{obj.__class__.__name__}" == path

    # Test that default finalizer is used
    assert_path_is(get_finalizer(account), settings.finalizer.module)

    account.finalizer = "my-finalizer"
    account.save()
    # Test alternative finalizer is used
    settings.alternative_finalizers = [
        AlternativeFinalizerSettings(
            id=account.finalizer,
            name="alt finalizer",
            description="My description!",
            finalizer=ACMEFinalizerSettings(
                directory="https://acme.edu/directory",
                account_kid="some-kid",
                account_hmac_key="some-key",
                account_email="noreply@acme.edu",
            ),
        )
    ]

    # Test that alternative finalizer is used
    assert_path_is(
        get_finalizer(account), settings.alternative_finalizers[0].finalizer.module
    )

    settings.alternative_finalizers = []
    # Test that default finalizer is used when no alt is found
    assert_path_is(get_finalizer(account), settings.finalizer.module)


@pytest.mark.django_db
@pytest.mark.parametrize("action", ["edit_finalizer", "edit_binding", "revoke-account"])
def test_view_all_accounts_permission(
    authenticated_web_client: Client, acme_newacct, action
):
    viewer = authenticated_web_client.test_user
    owner = gen_user()
    binding = db.AccountBinding.generate(owner, "other account", "original note")
    acme_newacct(with_eab=True, binding=binding, user=owner)
    binding.refresh_from_db()
    account = binding.bound_to
    account.finalizer = "original-finalizer"
    account.save()
    account_url = reverse("account", args=[binding.id])

    response = authenticated_web_client.get(reverse(Sections.Accounts.value))
    assert response.status_code == 200
    assert binding not in response.context["bindings"]["page"]
    assert authenticated_web_client.get(account_url).status_code == 403

    app_label, codename = Perms.VIEW_ALL_ACCOUNTS.split(".")
    viewer.user_permissions.add(
        Permission.objects.get(content_type__app_label=app_label, codename=codename)
    )

    response = authenticated_web_client.get(reverse(Sections.Accounts.value))
    assert response.status_code == 200
    assert binding in response.context["bindings"]["page"]

    response = authenticated_web_client.get(account_url)
    assert response.status_code == 200
    assert response.context["binding"] == binding
    assert not response.context["can_edit"]

    if action == "edit_finalizer":
        response = authenticated_web_client.post(
            reverse("api:edit_finalizer", args=[account.name]),
            {"id": None},
            content_type="application/json",
        )
    elif action == "edit_binding":
        response = authenticated_web_client.post(
            reverse("api:edit_binding", args=[binding.id]),
            {"name": "changed name", "note": "changed note"},
            content_type="application/json",
        )
    else:
        response = authenticated_web_client.post(account_url, {"revoke-account": "1"})

    binding.refresh_from_db()
    account.refresh_from_db()
    assert binding.name == "other account"
    assert binding.note == "original note"
    assert account.finalizer == "original-finalizer"
    assert account.status == AccountStatus.valid
    assert response.status_code == 403


@pytest.mark.django_db
def test_view_all_accounts_listings(authenticated_web_client: Client):
    viewer = authenticated_web_client.test_user
    bindings = []
    for owner in (viewer, gen_user(), gen_user()):
        for index in range(2):
            name = f"account-{owner.pk}-{index}"
            binding = db.AccountBinding.generate(owner, name)
            binding.bind_to(
                db.Account.objects.create(
                    name=name,
                    status=AccountStatus.valid,
                    jwk="{}",
                    jwk_thumbprint=name,
                )
            )
            bindings.append(binding)

    for binding in bindings:
        # assert that the viewer can only view their own created bindings at first
        assert bool(binding.accessible_by(viewer)) == (binding.creator_id == viewer.pk)

    app_label, codename = Perms.VIEW_ALL_ACCOUNTS.split(".")
    viewer.user_permissions.add(
        Permission.objects.get(content_type__app_label=app_label, codename=codename)
    )
    viewer.refresh_from_db()
    viewer = type(viewer).objects.get(pk=viewer.pk)

    # after adding the view all accounts permission, assert the viewer can
    # now see all bindings
    assert all(binding.accessible_by(viewer) for binding in bindings)
    assert set(db.AccountBinding.objects.by_user(viewer)) == set(bindings)
