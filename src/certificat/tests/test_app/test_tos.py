import pytest
from django.urls import reverse
from django.test import Client
from ..helpers import gen_user
from certificat.modules.acme import models as db


@pytest.mark.django_db
def test_anonymous(web_client: Client):
    response = web_client.get(reverse("edit-tos"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_logged_in(web_client: Client):
    user = gen_user()
    web_client.force_login(user)
    response = web_client.get(reverse("edit-tos"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_superuser(web_client: Client):
    user = gen_user(is_superuser=True)
    web_client.force_login(user)
    response = web_client.get(reverse("edit-tos"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_edit(authenticated_su_web_client: Client):
    text = "This is the new tos!"

    response = authenticated_su_web_client.post(reverse("edit-tos"), {"text": text})

    assert response.status_code == 302
    tos = db.TermsOfService.objects.order_by("-created_at").first()
    assert tos.text == text

    changed_text = "This is the new changed tos!"
    response = authenticated_su_web_client.post(
        reverse("edit-tos"), {"text": changed_text}
    )

    assert response.status_code == 302
    tos = db.TermsOfService.objects.order_by("-created_at").first()
    assert tos.text == changed_text
    assert db.TermsOfService.objects.count() == 2
