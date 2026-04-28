# -*- coding: utf-8 -*-
"""urls for acme django database"""

from django.urls import path

from . import views

app_name = "api"
urlpatterns = [
    path(
        "binding/<binding_name>",
        views.edit_binding,
        name="edit_binding",
    ),
    path(
        "my/groups",
        views.my_groups,
        name="fetch_user_groups",
    ),
    path("cert-activity", views.cert_activity, name="cert_activity"),
    path("order/<order_name>/events", views.order_events, name="order_events"),
]
