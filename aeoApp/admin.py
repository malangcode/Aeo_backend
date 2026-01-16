from django.contrib import admin
from .models import BrandProfile, Competitors, SecondaryBrands


@admin.register(BrandProfile)
class BrandProfileAdmin(admin.ModelAdmin):
    list_display = (
        "brand_name",
        "domain_name",
        "url",
        "created_at",
    )



@admin.register(Competitors)
class CompetitorsAdmin(admin.ModelAdmin):
    list_display = (
        "brand_name",
        "domain_name",
        "url",
        "created_at",
    )
    
    
@admin.register(SecondaryBrands)
class SecondaryBrandsAdmin(admin.ModelAdmin):
    list_display = (
        "brand_name",
        "domain_name",
        "url",
        "created_at",
    )