from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.conf import settings
from urllib.parse import urlparse, parse_qs


class BrandProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='brand_profile')
    
    brand_name = models.CharField(max_length=255)
    domain_name = models.CharField(max_length=255)
    url = models.URLField(max_length=255, default='https://www.google.com/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_brand_created = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Brand Profile"
        verbose_name_plural = "Brand Profiles"

    def __str__(self):
        return self.brand_name


class SecondaryBrands(models.Model):
    brand_profile = models.ForeignKey(BrandProfile, on_delete=models.CASCADE, related_name='secondary_brands')
    brand_name = models.CharField(max_length=255)
    domain_name = models.CharField(max_length=255)
    url = models.URLField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.brand_name



class Competitors(models.Model):
    brand_profile = models.ForeignKey(BrandProfile, on_delete=models.CASCADE, related_name='competitors')
    brand_name = models.CharField(max_length=255)
    domain_name = models.CharField(max_length=255)
    url = models.URLField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
      
    def __str__(self):
        return self.brand_name
    
    


class PromptHistory(models.Model):
    brand_profile = models.ForeignKey(
        BrandProfile,
        on_delete=models.CASCADE,
        related_name="prompt_history"
    )

    prompt = models.TextField()

    ai_response = models.TextField()

    # Visibility flags
    user_brand_mentioned = models.BooleanField(default=False)
    competitor_mentioned = models.BooleanField(default=False)

    # Structured mentions
    mentioned_brands = models.JSONField(default=list)
    mentioned_domains = models.JSONField(default=list)

    # Source classification
    SOURCE_CHOICES = (
        ("LLM", "LLM Knowledge"),
        ("SEARCH", "Search AI"),
    )
    source_type = models.CharField(
        max_length=10,
        choices=SOURCE_CHOICES
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.prompt
    
    
    


class BrandMentionMetric(models.Model):
    brand_profile = models.ForeignKey(
        BrandProfile,
        on_delete=models.CASCADE,
        related_name="mention_metrics"
    )

    brand_name = models.CharField(max_length=255)

    total_mentions = models.PositiveIntegerField(default=0)

    last_mentioned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("brand_profile", "brand_name")

    def __str__(self):
        return f"{self.brand_name} - {self.total_mentions}"
    
    
    


class BrandMentionTimeseries(models.Model):
    brand_profile = models.ForeignKey(
        BrandProfile,
        on_delete=models.CASCADE,
        related_name="timeseries"
    )

    brand_name = models.CharField(max_length=255)

    date = models.DateField()

    mentions = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("brand_profile", "brand_name", "date")
        ordering = ["date"]
    