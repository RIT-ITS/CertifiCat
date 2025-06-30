from django.contrib import admin
from ..acme.models import Authorization, Order, Usage, Certificate
from django.db.models import Q
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from django.utils import dateparse


@admin.register(Usage)
class AuthorAdmin(admin.ModelAdmin):
    pass


class AuthorizationInline(admin.TabularInline):
    model = Authorization


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["created_at", "expires", "name", "status", "identifiers"]
    list_display_links = [
        "name",
    ]
    inlines = [AuthorizationInline]

    search_fields = ["name"]
    search_help_text = "Search by comma-separated identifier or order name."

    def get_search_results(self, request, queryset, search_term):
        queryset, may_have_duplicates = super().get_search_results(
            request,
            queryset,
            search_term,
        )
        if search_term:
            query_filter = Q()
            for identifier in search_term.split(","):
                query_filter |= Q(identifiers__value__iexact=identifier.strip())

            queryset |= self.model.objects.filter(query_filter)

        return queryset.distinct(), may_have_duplicates

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("identifiers")

    def identifiers(self, model):
        return ", ".join(i.value for i in model.identifiers.all())

    def has_add_permission(self, request, obj=...):
        return False

    def has_delete_permission(self, request, obj=...):
        return False

    def has_change_permission(self, request, obj=...):
        return False


class CertificateExportResource(resources.ModelResource):
    sans = fields.Field()
    expiration = fields.Field()

    def dehydrate_sans(self, certificate):
        return ",".join(certificate.metadata.get("sans"))

    def dehydrate_expiration(self, certificate):
        return certificate.metadata.get("not_valid_after")

    class Meta:
        model = Certificate
        fields = ("id", "order__name", "created_at", "expiration", "sans", "chain")


@admin.register(Certificate)
class CertificateAdmin(ImportExportModelAdmin):
    list_display = ["created_at", "expiration", "order__name", "sans"]
    list_display_links = [
        "order__name",
    ]
    date_hierarchy = "created_at"
    search_fields = ["order__name"]
    search_help_text = "Search by comma-separated identifier or order name."
    readonly_fields = [field.name for field in Certificate._meta.get_fields()]
    resource_classes = [CertificateExportResource]

    def get_search_results(self, request, queryset, search_term):
        queryset, may_have_duplicates = super().get_search_results(
            request,
            queryset,
            search_term,
        )
        if search_term:
            query_filter = Q()
            for identifier in search_term.split(","):
                query_filter |= Q(order__identifiers__value__iexact=identifier.strip())

            queryset |= self.model.objects.filter(query_filter)

        return queryset.distinct(), may_have_duplicates

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("order")

    def expiration(self, model):
        return dateparse.parse_datetime(model.metadata.get("not_valid_after"))

    expiration.admin_order_field = "metadata__not_valid_after"

    def sans(self, model):
        return ", ".join(model.metadata.get("sans"))

    def has_add_permission(self, request, obj=...):
        return False

    def has_delete_permission(self, request, obj=...):
        return False

    def has_change_permission(self, request, obj=...):
        return False

    def has_import_permission(self, *args, **kwargs):
        return False
