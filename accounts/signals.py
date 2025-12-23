import logging
import os
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import translation
from .models import CustomUser
from products.models import Package

logger = logging.getLogger(__name__)

@receiver(post_save, sender=CustomUser)
def assign_free_package(sender, instance, created, **kwargs):
    if created:
        try:
            free_package = Package.objects.get(is_default_free=True)
            instance.packages.add(free_package)
        except Package.DoesNotExist:
            logger.warning("No default free package found. Please mark one in the admin.")
        except Package.MultipleObjectsReturned:
            logger.error("Multiple default free packages found. Please ensure only one is marked.")


