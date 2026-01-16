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