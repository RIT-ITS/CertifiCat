from django.contrib import admin
from ..acme.models import Usage


@admin.register(Usage)
class AuthorAdmin(admin.ModelAdmin):
    pass
