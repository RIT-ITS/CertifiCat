from django.urls import path, re_path

from certificat.settings.dynamic import ApplicationSettings

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
    # redirect requests for the account endpoint to the web managment endpoint
    path("acct/<acct_id>", views.acct_redirect, name="acct-redirect"),
]

# Anything else under the ACME root gets a 404. Skipped when ACME is
# mounted at the site root, where it would shadow every URL registered after it
# (the directory, health checks, etc.).
if ApplicationSettings.get().web_acme_mountpoint:
    urlpatterns.append(re_path(r"^(?P<path>.*)$", views.not_found, name="not-found"))
