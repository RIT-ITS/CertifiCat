import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize("method", ["get", "post", "head"])
@pytest.mark.parametrize("suffix", ["doesNotExist", "order/abc/nope", "newAcct/", ""])
def test_unknown_endpoint_returns_404(method, suffix):
    acme_root = reverse("acme:new-nonce").removesuffix("newNonce")
    response = getattr(Client(), method)(acme_root + suffix)

    assert response.status_code == 404
    assert response["Content-Type"] != "application/problem+json"
    if method != "head":
        assert response.content == b"404 page not found"


@pytest.mark.django_db
def test_known_endpoints_still_resolve():
    client = Client()
    assert client.head(reverse("acme:new-nonce")).status_code == 200
    assert client.get(reverse("directory")).status_code == 200
    assert reverse("acme:not-found", args=["x"]).endswith("/x")
