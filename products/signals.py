from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserPurchase

@receiver(post_save, sender=UserPurchase)
def grant_package_access(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        product = instance.product
        for package in product.packages.all():
            user.packages.add(package)
