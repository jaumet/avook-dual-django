from django.db import migrations

def create_account_confirmation_template(apps, schema_editor):
    EmailTemplate = apps.get_model('post_office', 'EmailTemplate')
    EmailTemplateTranslation = apps.get_model('post_office', 'EmailTemplateTranslation')

    template = EmailTemplate.objects.create(name='account_confirmation')

    EmailTemplateTranslation.objects.create(
        template=template,
        language='en',
        subject='Activate Your Account',
        body='<h1>Hi {{ user.first_name }},</h1><p>Please click the link below to activate your account:</p><p><a href="{{ token_url }}">{{ token_url }}</a></p>',
        plain_body='Hi {{ user.first_name }},\n\nPlease use the following link to activate your account:\n{{ token_url }}'
    )

    EmailTemplateTranslation.objects.create(
        template=template,
        language='ca',
        subject='Activa el teu compte',
        body='<h1>Hola {{ user.first_name }},</h1><p>Si us plau, fes clic a l\'enllaç següent per activar el teu compte:</p><p><a href="{{ token_url }}">{{ token_url }}</a></p>',
        plain_body='Hola {{ user.first_name }},\n\nSi us plau, fes servir el següent enllaç per activar el teu compte:\n{{ token_url }}'
    )

    EmailTemplateTranslation.objects.create(
        template=template,
        language='es',
        subject='Activa tu cuenta',
        body='<h1>Hola {{ user.first_name }},</h1><p>Por favor, haz clic en el siguiente enlace para activar tu cuenta:</p><p><a href="{{ token_url }}">{{ token_url }}</a></p>',
        plain_body='Hola {{ user.first_name }},\n\nPor favor, usa el siguiente enlace para activar tu cuenta:\n{{ token_url }}'
    )

class Migration(migrations.Migration):

    dependencies = [
        ('post_office', '0002_emailtemplatetranslation_plain_body'),
    ]

    operations = [
        migrations.RunPython(create_account_confirmation_template),
    ]
