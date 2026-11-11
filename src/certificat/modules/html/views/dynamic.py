import logging

import markdown
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.forms import Form
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from certificat.modules.acme.models import (
    MarkdownDisplay,
    TermsOfService,
    Usage,
)
from certificat.modules.html.forms import (
    TermsOfServiceEditForm,
    UsageEditForm,
)
from certificat.modules.perms import Gates, PermissionGate

from ..nav import Sections, build_breadcrumbs
from .base import ViewBase

logger = logging.getLogger(__name__)


class EditDynamicPageView(ViewBase):
    """Generic view used to edit the dynamic pages, such as usage or
    terms of service.

    This is an abstract class.
    """

    route_name: str = None
    display_name: str = None
    model_klass: type[MarkdownDisplay] = None
    edit_form_klass: type[Form] = None
    gate: Gates = None

    def test_func(self):
        return PermissionGate.evaluate(self.request.user, self.gate)

    def get_breadcrumbs(self, **kwargs):
        return build_breadcrumbs((self.display_name, reverse(self.route_name)), "Edit")

    def get(self, request: HttpRequest):
        last_page = self.model_klass.objects.order_by("-created_at").first()
        obj_form = self.edit_form_klass(
            initial={"text": last_page.text if last_page else ""},
            label_suffix="",
        )
        context = self.get_context_data(
            form=obj_form, display_name=self.display_name, route_name=self.route_name
        )
        return render(request, "certificat/edit-dynamic-page.html", context)

    def post(self, request: HttpRequest):
        obj_form = self.edit_form_klass(request.POST)
        if obj_form.is_valid():
            try:
                obj_form.save(request)
                messages.success(request, "Successfully saved edits.")
                return HttpResponseRedirect(reverse(self.route_name))
            except:  # noqa: E722
                messages.error(request, "There was an error saving your edits.")
                logger.exception("Error saving edits")

        context = self.get_context_data(
            form=obj_form, display_name=self.display_name, route_name=self.route_name
        )
        return render(request, "certificat/edit-dynamic-page.html", context)


class DynamicPageView(ViewBase):
    """Generic view used to display dynamic pages.

    This is an abstract class.
    """

    edit_route_name: str = None
    display_name: str = None
    model_klass: type[MarkdownDisplay] = None

    def user_can_edit(self):
        content_type = ContentType.objects.get_for_model(self.model_klass)
        return self.request.user.has_perm(
            f"{content_type.app_label}.change_{content_type.model}"
        )

    def get_breadcrumbs(self, **kwargs):
        return build_breadcrumbs(self.display_name)

    def get(self, request: HttpRequest):
        last_page = self.model_klass.objects.order_by("-created_at").first()
        parsed_markdown = ""
        if last_page:
            parsed_markdown = markdown.markdown(last_page.text)

        context = self.get_context_data(
            text=parsed_markdown,
            display_name=self.display_name,
            edit_route_name=self.edit_route_name,
            can_edit=self.user_can_edit(),
        )
        return render(request, "certificat/dynamic-page.html", context)


class UsageView(DynamicPageView):
    section = Sections.Usage
    edit_route_name = "edit-usage"
    display_name = "Usage"
    model_klass = Usage


class EditUsageView(EditDynamicPageView):
    section = Sections.Usage
    route_name = "USAGE"
    display_name = "Usage"
    model_klass = Usage
    edit_form_klass = UsageEditForm
    gate = Gates.EDIT_USAGE


class TermsOfServiceView(DynamicPageView):
    section = Sections.TOS
    edit_route_name = "edit-tos"
    display_name = "Terms of Service"
    model_klass = TermsOfService


class EditTermsOfServiceView(EditDynamicPageView):
    route_name = "TOS"
    display_name = "Terms of Service"
    model_klass = TermsOfService
    edit_form_klass = TermsOfServiceEditForm
    gate = Gates.EDIT_TOS
