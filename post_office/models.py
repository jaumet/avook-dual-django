from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.conf import settings

class EmailTemplate(models.Model):
    name = models.CharField(max_length=255, unique=True, help_text="A unique name to identify the template, e.g., 'account_confirmation'.")

    def __str__(self):
        return self.name

class EmailTemplateTranslation(models.Model):
    template = models.ForeignKey(EmailTemplate, related_name='translations', on_delete=models.CASCADE)
    language = models.CharField(max_length=10, choices=settings.LANGUAGES)
    subject = models.CharField(max_length=255)
    body = CKEditor5Field()

    class Meta:
        unique_together = ('template', 'language')

    def __str__(self):
        return f"{self.template.name} ({self.get_language_display()})"
