from django.contrib import admin
from .models import BrandProfile


@admin.register(BrandProfile)
class BrandProfileAdmin(admin.ModelAdmin):
    list_display = (
        "brand_name",
        "domain_name",
        "competitor1_brand_name",
        "competitor2_brand_name",
        "created_at",
    )

    list_filter = ("created_at",)
    search_fields = (
        "brand_name",
        "domain_name",
        "competitor1_brand_name",
        "competitor2_brand_name",
    )

    ordering = ("-created_at",)

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Brand Information", {
            "fields": ("brand_name", "domain_name")
        }),
        ("Competitor 1", {
            "fields": ("competitor1_brand_name", "competitor1_domain_name")
        }),
        ("Competitor 2", {
            "fields": ("competitor2_brand_name", "competitor2_domain_name")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
        ("flags", {
            "fields": ("is_brand_created",)
        }),
    )
