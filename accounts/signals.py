import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser
from products.models import Package

logger = logging.getLogger(__name__)

@receiver(post_save, sender=CustomUser)
def assign_free_package(sender, instance, created, **kwargs):
    if created:
        try:
            free_package = Package.objects.get(name="Pack-free")
            instance.packages.add(free_package)
        except Package.DoesNotExist:
            logger.warning("The 'Pack-free' package does not exist. Please create it in the admin.")
