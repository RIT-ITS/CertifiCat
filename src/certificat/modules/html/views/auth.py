import logging
from csv import Error

import inject
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse

from certificat.settings.dynamic import ApplicationSettings, RemoteAuthSettings

from ..nav import BreadCrumb, BreadCrumbs, Sections

logger = logging.getLogger(__name__)


class LocalLoginView(LoginView):
    def get_context_data(self, **kwargs):
        breadcrumbs = BreadCrumbs(
            [
                BreadCrumb("CertifiCat", reverse(Sections.Dashboard.value)),
                BreadCrumb("Login"),
            ]
        )
        return super().get_context_data(breadcrumbs=breadcrumbs, **kwargs)


class LocalLogoutView(LogoutView):
    http_method_names = ["get", "post", "options"]  # noqa: RUF012

    def get_context_data(self, **kwargs):
        breadcrumbs = BreadCrumbs(
            [
                BreadCrumb("CertifiCat", reverse(Sections.Dashboard.value)),
                BreadCrumb("Logout"),
            ]
        )
        return super().get_context_data(breadcrumbs=breadcrumbs, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs):
        from django.contrib.auth import logout as auth_logout

        auth_logout(request)
        context = self.get_context_data()
        return render(request, "certificat/logout.html", context=context)


def acs_failure(request: HttpRequest, exception: Error, status, **kwargs):
    attributes = kwargs.get("session_info", {}).get("ava")
    logger.exception(exception)
    logger.info(kwargs)

    return render(
        request,
        "certificat/acs_error.html",
        {
            "attributes": attributes,
            "exception": exception,
            "saml_settings": inject.instance(ApplicationSettings).authentication,
        },
    )


def remote_login_redirect(request: HttpRequest, *args, **kwargs):
    app_settings = inject.instance(ApplicationSettings)

    if app_settings.authentication.type != "remote":
        raise Exception("What are you doing?")  # noqa: TRY002

    redirect_target = request.GET.get("next", app_settings.web_ui_mountpoint)
    remote_auth_settings: RemoteAuthSettings = app_settings.authentication

    return redirect(
        remote_auth_settings.redirect_template.format(redirect=redirect_target)
    )
