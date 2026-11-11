import logging

import inject
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpRequest
from django.shortcuts import render
from django.views import View
from django.views.generic.base import ContextMixin

from certificat.modules.perms import PermissionDeniedError
from certificat.settings.dynamic import ApplicationSettings

from ..nav import BreadCrumbs

logger = logging.getLogger(__name__)


class ViewBase(UserPassesTestMixin, ContextMixin, View):
    """
    Base view for all views. By default every user must be authenticated
    to use the site.
    """

    settings: ApplicationSettings = inject.attr(ApplicationSettings)

    def test_func(self):
        return self.request.user.is_authenticated

    def get_breadcrumbs(self, **kwargs) -> BreadCrumbs:
        return BreadCrumbs()

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            breadcrumbs=self.get_breadcrumbs(**kwargs), **kwargs
        )

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except PermissionDeniedError:
            return self.handle_no_permission()

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return render(self.request, "certificat/no-permission.html", status=403)
        else:
            return super().handle_no_permission()


def handler404(request: HttpRequest, *args, **argv):
    return render(request, "certificat/404.html", {}, status=404)


def handler500(request: HttpRequest, *args, **argv):
    return render(request, "certificat/500.html", {}, status=500)
