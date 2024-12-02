from django.contrib import admin
from django.urls import path
from . import views
from .nav import Sections

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.IndexView.as_view(), name=Sections.Dashboard.value),
    path("account/<binding_id>", views.AccountView.as_view(), name="account"),
    path("accounts/", views.AccountsView.as_view(), name=Sections.Accounts.value),
    path("order/<order_id>", views.OrderView.as_view(), name="order"),
    path("usage/", views.UsageView.as_view(), name=Sections.Usage.value),
    path(
        "certificates/",
        views.CertificatesView.as_view(),
        name=Sections.Certificates.value,
    ),
    path(
        "certificate/<cert_id>",
        views.CertificateView.as_view(),
        name="certificate",
    ),
    path("terms-of-service/", views.TermsOfService.as_view(), name=Sections.TOS.value),
    path("login/", views.LocalLoginView.as_view(), name="login"),
    path("logout/", views.LocalLogoutView.as_view(), name="logout"),
    path("admin/", views.IndexView.as_view(), name=Sections.Admin.value),
]
