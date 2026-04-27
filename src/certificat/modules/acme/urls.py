from django.urls import path
from . import views

app_name = "acme"


urlpatterns = [
    path("newNonce", views.newNonce, name="new-nonce"),
    path("newAcct", views.newAccount, name="new-account"),
    path("newOrder", views.newOrder, name="new-order"),
    path("authz/<authz_id>", views.authz, name="authz"),
    path("chall/<chall_id>", views.chall, name="chall"),
    path("order/<order_id>", views.order, name="order"),
    path("order/<order_id>/finalize", views.finalize, name="finalize"),
    path("cert/<cert_id>", views.cert, name="cert"),
]
