from django.urls import path, re_path, include
from . import views

app_name = "acme"

acme_resource_patterns = (
    [
        path("newNonce", views.newNonce),
        path("newAccount", views.newAccount),
        path("newOrder", views.newOrder),
        path("authz/<authz_id>", views.authz),
        path("chall/<chall_id>", views.chall),
        path("order/<order_id>", views.order),
        path("order/<order_id>/finalize", views.finalize),
        path("cert/<cert_id>", views.cert),
    ],
    "acme",
)

urlpatterns = [
    # Support optional trailing slash for difficult clients
    re_path(r"directory/?", views.directory),
    path("acme/", include(acme_resource_patterns)),
]
