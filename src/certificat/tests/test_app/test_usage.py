import pytest
from django.urls import reverse
from django.test import Client
from ..helpers import gen_user
from certificat.modules.acme import models as db


@pytest.mark.django_db
def test_anonymous(web_client: Client):
    response = web_client.get(reverse("edit-usage"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_logged_in(web_client: Client):
    user = gen_user()
    web_client.force_login(user)
    response = web_client.get(reverse("edit-usage"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_superuser(web_client: Client):
    user = gen_user(is_superuser=True)
    web_client.force_login(user)
    response = web_client.get(reverse("edit-usage"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_edit(authenticated_su_web_client: Client):
    text = "This is the new usage!"

    response = authenticated_su_web_client.post(reverse("edit-usage"), {"usage": text})

    assert response.status_code == 302
    usage = db.Usage.objects.order_by("-created_at").first()
    assert usage.text == text

    changed_text = "This is the new changed usage!"
    response = authenticated_su_web_client.post(
        reverse("edit-usage"), {"usage": changed_text}
    )

    assert response.status_code == 302
    usage = db.Usage.objects.order_by("-created_at").first()
    assert usage.text == changed_text
    assert db.Usage.objects.count() == 2
