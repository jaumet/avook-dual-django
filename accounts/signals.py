import logging
import os
from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import translation
from django.utils.html import strip_tags
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


@receiver(post_save, sender=CustomUser)
def send_confirmation_email(sender, instance, created, **kwargs):
    if created and not instance.is_staff and instance.confirmation_token:
        # Activate the default language to build the URL with the correct prefix
        with translation.override(settings.LANGUAGE_CODE):
            # Use reverse to build the URL safely
            activation_path = reverse('accounts:activate', kwargs={'token': instance.confirmation_token})

        # Get the domain from an environment variable for flexibility in production
        domain = os.environ.get('SITE_DOMAIN', '127.0.0.1:8000')
        protocol = 'https' if not settings.DEBUG else 'http'
        token_url = f"{protocol}://{domain}{activation_path}"

        context = {
            'user': instance,
            'token_url': token_url,
        }

        # Render the HTML and plain text versions of the email
        html_message = render_to_string('emails/account_confirmation.html', context)
        plain_message = strip_tags(html_message)

        # Send the email
        send_mail(
            'Confirma el teu compte a Audiovook',
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
            html_message=html_message
        )
