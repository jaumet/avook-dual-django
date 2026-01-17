from django.db import migrations

def seed_password_reset_template(apps, schema_editor):
    EmailTemplate = apps.get_model('post_office', 'EmailTemplate')
    EmailTemplateTranslation = apps.get_model('post_office', 'EmailTemplateTranslation')

    template_name = 'password_reset'
    email_template, created = EmailTemplate.objects.get_or_create(name=template_name)

    translations = {
        'ca': {
            'subject': 'Restabliment de la contrasenya',
            'body': '<p>Hola {{ user.first_name }},</p><p>Hem rebut una sol·licitud per restablir la vostra contrasenya. Feu clic a l\'enllaç següent per triar-ne una de nova:</p><p><a href="{{ protocol }}://{{ domain }}{{ path }}">Restablir contrasenya</a></p><p>Si no heu sol·licitat aquest canvi, podeu ignorar aquest correu electrònic.</p><p>Gràcies,<br>L\'equip de Dual</p>',
            'plain_body': 'Hola {{ user.first_name }},\n\nHem rebut una sol·licitud per restablir la vostra contrasenya. Aneu a l\'enllaç següent per triar-ne una de nova:\n{{ protocol }}://{{ domain }}{{ path }}\n\nSi no heu sol·licitat aquest canvi, podeu ignorar aquest correu electrònic.\n\nGràcies,\nL\'equip de Dual'
        },
        'en': {
            'subject': 'Password Reset',
            'body': '<p>Hello {{ user.first_name }},</p><p>We received a request to reset your password. Click the link below to choose a new one:</p><p><a href="{{ protocol }}://{{ domain }}{{ path }}">Reset Password</a></p><p>If you did not request this change, you can ignore this email.</p><p>Thanks,<br>The Dual Team</p>',
            'plain_body': 'Hello {{ user.first_name }},\n\nWe received a request to reset your password. Go to the following link to choose a new one:\n{{ protocol }}://{{ domain }}{{ path }}\n\nIf you did not request this change, you can ignore this email.\n\nThanks,\nThe Dual Team'
        },
        'es': {
            'subject': 'Restablecimiento de contraseña',
            'body': '<p>Hola {{ user.first_name }},</p><p>Hemos recibido una solicitud para restablecer tu contraseña. Haz clic en el siguiente enlace para elegir una nueva:</p><p><a href="{{ protocol }}://{{ domain }}{{ path }}">Restablecer contraseña</a></p><p>Si no has solicitado este cambio, puedes ignorar este correo electrónico.</p><p>Gracias,<br>El equipo de Dual</p>',
            'plain_body': 'Hola {{ user.first_name }},\n\nHemos recibido una solicitud para restablecer tu contraseña. Ve al siguiente enlace para elegir una nueva:\n{{ protocol }}://{{ domain }}{{ path }}\n\nSi no has solicitado este cambio, puedes ignorar este correo electrónico.\n\nGracias,\nEl equipo de Dual'
        },
        'fr': {
            'subject': 'Réinitialisation du mot de passe',
            'body': '<p>Bonjour {{ user.first_name }},</p><p>Nous avons reçu une demande de réinitialisation de votre mot de passe. Cliquez sur le lien ci-dessous pour en choisir un nouveau :</p><p><a href="{{ protocol }}://{{ domain }}{{ path }}">Réinitialiser le mot de passe</a></p><p>Si vous n\'avez pas demandé ce changement, vous pouvez ignorer cet e-mail.</p><p>Merci,<br>L\'équipe Dual</p>',
            'plain_body': 'Bonjour {{ user.first_name }},\n\nNous avons reçu une demande de réinitialisation de votre mot de passe. Allez sur le lien suivant pour en choisir un nouveau :\n{{ protocol }}://{{ domain }}{{ path }}\n\nSi vous n\'avez pas demandé ce changement, vous pouvez ignorer cet e-mail.\n\nMerci,\nL\'équipe Dual'
        },
        'de': {
            'subject': 'Passwort zurücksetzen',
            'body': '<p>Hallo {{ user.first_name }},</p><p>Wir haben eine Anfrage zum Zurücksetzen Ihres Passworts erhalten. Klicken Sie auf den folgenden Link, um ein neues zu wählen:</p><p><a href="{{ protocol }}://{{ domain }}{{ path }}">Passwort zurücksetzen</a></p><p>Wenn Sie diese Änderung nicht angefordert haben, können Sie diese E-Mail ignorieren.</p><p>Danke,<br>Das Dual-Team</p>',
            'plain_body': 'Hallo {{ user.first_name }},\n\nWir haben eine Anfrage zum Zurücksetzen Ihres Passworts erhalten. Gehen Sie zum folgenden Link, um ein neues zu wählen:\n{{ protocol }}://{{ domain }}{{ path }}\n\nWenn Sie diese Änderung nicht angefordert haben, können Sie diese E-Mail ignorieren.\n\nDanke,\nDas Dual-Team'
        },
        'it': {
            'subject': 'Reimpostazione della password',
            'body': '<p>Ciao {{ user.first_name }},</p><p>Abbiamo ricevuto una richiesta di reimpostazione della password. Fai clic sul link qui sotto per sceglierne una nuova:</p><p><a href="{{ protocol }}://{{ domain }}{{ path }}">Reimposta password</a></p><p>Se non hai richiesto questa modifica, puoi ignorare questa email.</p><p>Grazie,<br>Il Team Dual</p>',
            'plain_body': 'Ciao {{ user.first_name }},\n\nAbbiamo ricevuto una richiesta di reimpostazione della password. Vai al seguente link per sceglierne una nuova:\n{{ protocol }}://{{ domain }}{{ path }}\n\nSe non hai richiesto questa modifica, puoi ignorare questa email.\n\nGrazie,\nIl Team Dual'
        },
        'pt': {
            'subject': 'Redefinição de senha',
            'body': '<p>Olá {{ user.first_name }},</p><p>Recebemos um pedido para redefinir sua senha. Clique no link abaixo para escolher uma nova:</p><p><a href="{{ protocol }}://{{ domain }}{{ path }}">Redefinir senha</a></p><p>Se você não solicitou esta alteração, pode ignorar este e-mail.</p><p>Obrigado,<br>A Equipe Dual</p>',
            'plain_body': 'Olá {{ user.first_name }},\n\nRecebemos um pedido para redefinir sua senha. Vá para o seguinte link para escolher uma nova:\n{{ protocol }}://{{ domain }}{{ path }}\n\nSe você não solicitou esta alteração, pode ignorar este e-mail.\n\nObrigado,\nA Equipe Dual'
        }
    }

    for lang, data in translations.items():
        EmailTemplateTranslation.objects.get_or_create(
            template=email_template,
            language=lang,
            defaults=data
        )

def unseed_password_reset_template(apps, schema_editor):
    EmailTemplate = apps.get_model('post_office', 'EmailTemplate')
    EmailTemplate.objects.filter(name='password_reset').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('post_office', '0003_account_confirmation_template'),
    ]

    operations = [
        migrations.RunPython(seed_password_reset_template, unseed_password_reset_template),
    ]
