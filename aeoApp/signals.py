from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import BrandProfile


@receiver(post_save, sender=User)
def create_or_update_brand_profile(sender, instance, created, **kwargs):
    BrandProfile.objects.get_or_create(user=instance)
    


@receiver(post_save, sender=BrandProfile)
def mark_brand_created_on_first_update(sender, instance, created, **kwargs):
    """
    Set is_brand_created = True only after the first UPDATE,
    not on initial creation.
    """

    # If just created, do nothing
    if created:
        return

    # If already marked, do nothing
    if instance.is_brand_created:
        return

    # Mark brand as created
    BrandProfile.objects.filter(pk=instance.pk).update(is_brand_created=True)    