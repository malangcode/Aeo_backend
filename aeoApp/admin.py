from django.contrib import admin
from .models import BrandMentionMetric, BrandMentionTimeseries, BrandProfile, Competitors, PromptHistory, SecondaryBrands


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
    
    
    
@admin.register(PromptHistory)
class PromptHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "brand_profile",
        "prompt",
        "ai_response",
        "user_brand_mentioned",
        "competitor_mentioned",     
    )



@admin.register(BrandMentionMetric)
class BrandMentionMetricAdmin(admin.ModelAdmin):
    list_display = (
        "brand_profile",
        "brand_name",
        "total_mentions",
        "last_mentioned_at",
    )



@admin.register(BrandMentionTimeseries)
class BrandMentionTimeseriesAdmin(admin.ModelAdmin):
    list_display = (
        "brand_profile",
        "brand_name",
        "date",
        "mentions",
    )
    
    
 

    