from rest_framework import serializers
from .models import BrandProfile, Competitors, SecondaryBrands


class BrandProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandProfile
        exclude = ("user", "created_at", "updated_at")


class CompetitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competitors
        fields = [
            'id',
            'brand_name',
            'domain_name',
            'url',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'brand_profile', 'updated_at']
        
        
        
class SecondaryBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecondaryBrands
        fields = "__all__"
        read_only_fields = ( "brand_profile", "created_at")        