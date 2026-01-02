import logging
from django.conf import settings
from django.core.mail import send_mail
from django.template import Context, Template
from django.utils import translation
from .models import EmailTemplate

logger = logging.getLogger(__name__)

def send_templated_email(template_name, context, to_email, from_email=None, language=None):
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL

    if language is None:
        language = translation.get_language() or settings.LANGUAGE_CODE
    language_code = language.split('-')[0]

    try:
        template = EmailTemplate.objects.get(name=template_name)

        translation_obj = template.translations.filter(language=language_code).first()
        if not translation_obj:
            fallback_lang = settings.LANGUAGE_CODE.split('-')[0]
            translation_obj = template.translations.filter(language=fallback_lang).first()
            if not translation_obj:
                 # As a last resort, get the first available translation
                translation_obj = template.translations.first()

        if not translation_obj:
            logger.error(f"No translations found for email template '{template_name}'.")
            return

        subject_template = Template(translation_obj.subject)
        body_template = Template(translation_obj.body)

        subject = subject_template.render(Context(context))
        html_message = body_template.render(Context(context))

        send_mail(
            subject,
            html_message,
            from_email,
            [to_email],
            html_message=html_message
        )
    except EmailTemplate.DoesNotExist:
        logger.error(f"Email template '{template_name}' not found.")
