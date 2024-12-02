from django.contrib import admin
from ..acme.models import TempUsageHack


@admin.register(TempUsageHack)
class AuthorAdmin(admin.ModelAdmin):
    pass
