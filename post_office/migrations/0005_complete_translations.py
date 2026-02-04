from django.db import migrations

def complete_translations(apps, schema_editor):
    EmailTemplate = apps.get_model('post_office', 'EmailTemplate')
    EmailTemplateTranslation = apps.get_model('post_office', 'EmailTemplateTranslation')

    # 1. account_confirmation
    ac_template, _ = EmailTemplate.objects.get_or_create(name='account_confirmation')
    ac_translations = {
        'ca': {
            'subject': 'Activa el teu compte',
            'body': '<h1>Hola {{ user.first_name }},</h1><p>Si us plau, fes clic a l\'enllaç següent per activar el teu compte:</p><p><a href="{{ activate_url }}">{{ activate_url }}</a></p>',
            'plain_body': 'Hola {{ user.first_name }},\n\nSi us plau, fes servir el següent enllaç per activar el teu compte:\n{{ activate_url }}'
        },
        'en': {
            'subject': 'Activate Your Account',
            'body': '<h1>Hi {{ user.first_name }},</h1><p>Please click the link below to activate your account:</p><p><a href="{{ activate_url }}">{{ activate_url }}</a></p>',
            'plain_body': 'Hi {{ user.first_name }},\n\nPlease use the following link to activate your account:\n{{ activate_url }}'
        },
        'es': {
            'subject': 'Activa tu cuenta',
            'body': '<h1>Hola {{ user.first_name }},</h1><p>Por favor, haz clic en el siguiente enlace para activar tu cuenta:</p><p><a href="{{ activate_url }}">{{ activate_url }}</a></p>',
            'plain_body': 'Hola {{ user.first_name }},\n\nPor favor, usa el siguiente enlace para activar tu cuenta:\n{{ activate_url }}'
        },
        'fr': {
            'subject': 'Activez votre compte',
            'body': '<h1>Bonjour {{ user.first_name }},</h1><p>Veuillez cliquer sur le lien ci-dessous pour activer votre compte :</p><p><a href="{{ activate_url }}">{{ activate_url }}</a></p>',
            'plain_body': 'Bonjour {{ user.first_name }},\n\nVeuillez utiliser le lien suivant pour activer votre compte :\n{{ activate_url }}'
        },
        'de': {
            'subject': 'Aktivieren Sie Ihr Konto',
            'body': '<h1>Hallo {{ user.first_name }},</h1><p>Bitte klicken Sie auf den folgenden Link, um Ihr Konto zu aktivieren:</p><p><a href="{{ token_url }}">{{ activate_url }}</a></p>',
            'plain_body': 'Hallo {{ user.first_name }},\n\nBitte verwenden Sie den folgenden Link, um Ihr Konto zu aktivieren:\n{{ activate_url }}'
        },
        'it': {
            'subject': 'Attiva il tuo account',
            'body': '<h1>Ciao {{ user.first_name }},</h1><p>Fai clic sul link qui sotto per attivare il tuo account:</p><p><a href="{{ activate_url }}">{{ activate_url }}</a></p>',
            'plain_body': 'Ciao {{ user.first_name }},\n\nUsa il seguente link per attivare il teu account:\n{{ activate_url }}'
        },
        'pt': {
            'subject': 'Ative sua conta',
            'body': '<h1>Olá {{ user.first_name }},</h1><p>Clique no link abaixo para ativar sua conta:</p><p><a href="{{ activate_url }}">{{ activate_url }}</a></p>',
            'plain_body': 'Olá {{ user.first_name }},\n\nUse o seguinte link para ativar sua conta:\n{{ activate_url }}'
        }
    }
    for lang, data in ac_translations.items():
        EmailTemplateTranslation.objects.update_or_create(template=ac_template, language=lang, defaults=data)

    # 2. purchase_confirmation
    pc_template, _ = EmailTemplate.objects.get_or_create(name='purchase_confirmation')
    pc_translations = {
        'ca': {
            'subject': 'La teva compra s’ha activat a Dual',
            'body': '<p>Hola {{ user.first_name|default:user.username }},</p><p>La teva compra s\'ha activat correctament a Dual.</p><p><strong>Producte:</strong> {{ product_name }}</p><p><strong>Data de pagament:</strong> {{ payment_date }}</p><p>Pots accedir als teus continguts des del següent enllaç:</p><p><a href="{{ purchase_url }}">{{ purchase_url }}</a></p><p>Gràcies per confiar en Dual!</p>',
            'plain_body': 'Hola {{ user.first_name|default:user.username }},\n\nLa teva compra s\'ha activat correctament a Dual.\n\nProducte: {{ product_name }}\nData de pagament: {{ payment_date }}\n\nPots accedir als teus continguts des del següent enllaç:\n{{ purchase_url }}\n\nGràcies per confiar en Dual!'
        },
        'en': {
            'subject': 'Your purchase has been activated on Dual',
            'body': '<p>Hello {{ user.first_name|default:user.username }},</p><p>Your purchase has been successfully activated on Dual.</p><p><strong>Product:</strong> {{ product_name }}</p><p><strong>Payment date:</strong> {{ payment_date }}</p><p>You can access your content from the following link:</p><p><a href="{{ purchase_url }}">{{ purchase_url }}</a></p><p>Thank you for choosing Dual!</p>',
            'plain_body': 'Hello {{ user.first_name|default:user.username }},\n\nYour purchase has been successfully activated on Dual.\n\nProduct: {{ product_name }}\nPayment date: {{ payment_date }}\n\nYou can access your content from the following link:\n{{ purchase_url }}\n\nThank you for choosing Dual!'
        },
        'es': {
            'subject': 'Tu compra se ha activado en Dual',
            'body': '<p>Hola {{ user.first_name|default:user.username }},</p><p>Tu compra se ha activado correctamente en Dual.</p><p><strong>Producto:</strong> {{ product_name }}</p><p><strong>Fecha de pago:</strong> {{ payment_date }}</p><p>Puedes acceder a tus contenidos desde el siguiente enlace:</p><p><a href="{{ purchase_url }}">{{ purchase_url }}</a></p><p>¡Gracias por confiar en Dual!</p>',
            'plain_body': 'Hola {{ user.first_name|default:user.username }},\n\nTu compra se ha activado correctamente en Dual.\n\nProducto: {{ product_name }}\nFecha de pago: {{ payment_date }}\n\nPuedes acceder a tus contenidos desde el siguiente enlace:\n{{ purchase_url }}\n\n¡Gracias por confiar en Dual!'
        },
        'fr': {
            'subject': 'Votre achat a été activé sur Dual',
            'body': '<p>Bonjour {{ user.first_name|default:user.username }},</p><p>Votre achat a été activé avec succès sur Dual.</p><p><strong>Produit :</strong> {{ product_name }}</p><p><strong>Date de paiement :</strong> {{ payment_date }}</p><p>Vous pouvez accéder à vos contenus via le lien suivant :</p><p><a href="{{ purchase_url }}">{{ purchase_url }}</a></p><p>Merci de faire confiance à Dual !</p>',
            'plain_body': 'Bonjour {{ user.first_name|default:user.username }},\n\nVotre achat a été activé avec succès sur Dual.\n\nProduit : {{ product_name }}\nDate de paiement : {{ payment_date }}\n\nVous pouvez accéder à vos contenus via le lien suivant :\n{{ purchase_url }}\n\nMerci de faire confiance à Dual !'
        },
        'de': {
            'subject': 'Ihr Kauf wurde auf Dual aktiviert',
            'body': '<p>Hallo {{ user.first_name|default:user.username }},</p><p>Ihr Kauf wurde erfolgreich auf Dual aktiviert.</p><p><strong>Produkt:</strong> {{ product_name }}</p><p><strong>Zahlungsdatum:</strong> {{ payment_date }}</p><p>Sie können über den folgenden Link auf Ihre Inhalte zugreifen:</p><p><a href="{{ purchase_url }}">{{ purchase_url }}</a></p><p>Vielen Dank für Ihr Vertrauen in Dual!</p>',
            'plain_body': 'Hallo {{ user.first_name|default:user.username }},\n\nIhr Kauf wurde erfolgreich auf Dual aktiviert.\n\nProdukt: {{ product_name }}\nZahlungsdatum: {{ payment_date }}\n\nSie können über den folgenden Link auf Ihre Inhalte zugreifen:\n{{ purchase_url }}\n\nVielen Dank für Ihr Vertrauen in Dual!'
        },
        'it': {
            'subject': 'Il tuo acquisto è stato attivato su Dual',
            'body': '<p>Ciao {{ user.first_name|default:user.username }},</p><p>Il tuo acquisto è stato attivato con successo su Dual.</p><p><strong>Prodotto:</strong> {{ product_name }}</p><p><strong>Data del pagamento:</strong> {{ payment_date }}</p><p>Puoi accedere ai tuoi contenuti dal seguente link:</p><p><a href="{{ purchase_url }}">{{ purchase_url }}</a></p><p>Grazie per aver scelto Dual!</p>',
            'plain_body': 'Ciao {{ user.first_name|default:user.username }},\n\nIl tuo acquisto è stato attivato con successo su Dual.\n\nProdotto: {{ product_name }}\nData del pagamento: {{ payment_date }}\n\nPuoi accedere ai tuoi contenuti dal seguente link:\n{{ purchase_url }}\n\nGrazie per aver scelto Dual!'
        },
        'pt': {
            'subject': 'Sua compra foi ativada no Dual',
            'body': '<p>Olá {{ user.first_name|default:user.username }},</p><p>Sua compra foi ativada com sucesso no Dual.</p><p><strong>Produto:</strong> {{ product_name }}</p><p><strong>Data do pagamento:</strong> {{ payment_date }}</p><p>Você pode acessar seus conteúdos pelo seguinte link:</p><p><a href="{{ purchase_url }}">{{ purchase_url }}</a></p><p>Obrigado por confiar no Dual!</p>',
            'plain_body': 'Olá {{ user.first_name|default:user.username }},\n\nSua compra foi ativada com sucesso no Dual.\n\nProduto: {{ product_name }}\nData do pagamento: {{ payment_date }}\n\nVocê pode acessar seus conteúdos pelo seguinte link:\n{{ purchase_url }}\n\nObrigado por confiar no Dual!'
        }
    }
    for lang, data in pc_translations.items():
        EmailTemplateTranslation.objects.update_or_create(template=pc_template, language=lang, defaults=data)

    # 3. login_code
    lc_template, _ = EmailTemplate.objects.get_or_create(name='login_code')
    lc_translations = {
        'ca': {
            'subject': 'El teu enllaç màgic per a {{ site_name }}',
            'body': '<p>Hola,</p><p>Per iniciar la sessió, fes clic a l\'enllaç següent:</p><p><a href="{{ protocol }}://{{ domain }}{{ confirm_url }}?code={{ code }}">{{ protocol }}://{{ domain }}{{ confirm_url }}?code={{ code }}</a></p><p>O introdueix el següent codi a la pàgina d\'inici de sessió:</p><p>Codi: <strong>{{ code }}</strong></p><p>Aquest enllaç i codi caducaran en 10 minuts.</p>',
            'plain_body': 'Hola,\n\nPer iniciar la sessió, fes clic a l\'enllaç següent:\n{{ protocol }}://{{ domain }}{{ confirm_url }}?code={{ code }}\n\nO introdueix el següent codi a la pàgina d\'inici de sessió:\nCodi: {{ code }}\n\nAquest enllaç i codi caducaran en 10 minuts.'
        },
        'en': {
            'subject': 'Your Magic Link for {{ site_name }}',
            'body': '<p>Hello,</p><p>To log in, click the link below:</p><p><a href="{{ protocol }}://{{ domain }}{{ confirm_url }}?code={{ code }}">{{ protocol }}://{{ domain }}{{ confirm_url }}?code={{ code }}</a></p><p>Or enter the following code on the login page:</p><p>Code: <strong>{{ code }}</strong></p><p>This link and code will expire in 10 minutes.</p>',
            'plain_body': 'Hello,\n\nTo log in, click the link below:\n{{ protocol }}://{{ domain }}{{ confirm_url }}?code={{ code }}\n\nOr enter the following code on the login page:\nCode: {{ code }}\n\nThis link and code will expire in 10 minutes.'
        },
        'es': {
            'subject': 'Tu enlace mágico para {{ site_name }}',
            'body': '<p>Hola,</p><p>Para iniciar sesión, haz clic en el siguiente enlace:</p><p><a href="{{ protocol }}://{{ domain }}{{ confirm_url }}?code={{ code }}">{{ protocol }}://{{ domain }}{{ confirm_url }}?code={{ code }}</a></p><p>O introduce el siguiente código en la página de inicio de sesión:</p><p>Código: <strong>{{ code }}</strong></p><p>Este enlace y código caducarán en 10 minutos.</p>',
            'plain_body': 'Hola,\n\nPara iniciar sesión, haz clic en el siguiente enlace:\n{{ protocol }}://{{ domain }}{{ confirm_url }}?code={{ code }}\n\nO introduce el siguiente código en la página de inicio de sesión:\nCódigo: {{ code }}\n\nEste enlace y código caducarán en 10 minutos.'
        },
        'fr': {
            'subject': 'Votre lien magique pour {{ site_name }}',
            'body': '<p>Bonjour,</p><p>Pour vous connecter, cliquez sur le lien ci-dessous :</p><p><a href="{{ protocol }}://{{ domain }}{{ confirm_url }}?code={{ code }}">{{ protocol }}://{{ domain }}{{ confirm_url }}?code={{ code }}</a></p><p>Ou saisissez le code suivant sur la page de connexion :</p><p>Code : <strong>{{ code }}</strong></p><p>Ce lien et ce code expireront dans 10 minutes.</p>',
            'plain_body': 'Bonjour,\n\nPour vous connecter, cliquez sur le lien ci-dessous :\n{{ protocol }}://{{ domain }}{{ confirm_url }}?code={{ code }}\n\nOu saisissez le code suivant sur la page de connexion :\nCode : {{ code }}\n\nCe lien et ce code expireront dans 10 minutes.'
        },
        'de': {
            'subject': 'Ihr Magic Link für {{ site_name }}',
            'body': '<p>Hallo,</p><p>Um sich anzumelden, klicken Sie auf den folgenden Link:</p><p><a href="{{ protocol }}://{{ domain }}{{ confirm_url }}?code={{ code }}">{{ protocol }}://{{ domain }}{{ confirm_url }}?code={{ code }}</a></p><p>Oder geben Sie den folgenden Code auf der Anmeldeseite ein:</p><p>Code: <strong>{{ code }}</strong></p><p>Dieser Link und Code laufen in 10 Minuten ab.</p>',
            'plain_body': 'Hallo,\n\nUm sich anzumelden, klicken Sie auf den folgenden Link:\n{{ protocol }}://{{ domain }}{{ confirm_url }}?code={{ code }}\n\nOder geben Sie den folgenden Code auf der Anmeldeseite ein:\nCode: {{ code }}\n\nDieser Link und Code laufen in 10 Minuten ab.'
        },
        'it': {
            'subject': 'Il tuo Magic Link per {{ site_name }}',
            'body': '<p>Ciao,</p><p>Per accedere, fai clic sul link qui sotto:</p><p><a href="{{ protocol }}://{{ domain }}{{ confirm_url }}?code={{ code }}">{{ protocol }}://{{ domain }}{{ confirm_url }}?code={{ code }}</a></p><p>Oppure inserisci il seguente codice nella pagina di login:</p><p>Codice: <strong>{{ code }}</strong></p><p>Questo link e il codice scadranno tra 10 minuti.</p>',
            'plain_body': 'Ciao,\n\nPer accedere, fai clic sul link qui sotto:\n{{ protocol }}://{{ domain }}{{ confirm_url }}?code={{ code }}\n\nOppure inserisci il seguente codice nella pagina di login:\nCodice: {{ code }}\n\nQuesto link e il codice scadranno tra 10 minuti.'
        },
        'pt': {
            'subject': 'Seu Link Mágico para {{ site_name }}',
            'body': '<p>Olá,</p><p>Para fazer login, clique no link abaixo:</p><p><a href="{{ protocol }}://{{ domain }}{{ confirm_url }}?code={{ code }}">{{ protocol }}://{{ domain }}{{ confirm_url }}?code={{ code }}</a></p><p>Ou insira o seguinte código na página de login:</p><p>Código: <strong>{{ code }}</strong></p><p>Este link e código expirarão em 10 minutos.</p>',
            'plain_body': 'Olá,\n\nPara fazer login, clique no link abaixo:\n{{ protocol }}://{{ domain }}{{ confirm_url }}?code={{ code }}\n\nOu insira o seguinte código na página de login:\nCódigo: {{ code }}\n\nEste link e código expirarão em 10 minutos.'
        }
    }
    for lang, data in lc_translations.items():
        EmailTemplateTranslation.objects.update_or_create(template=lc_template, language=lang, defaults=data)

    # 4. account_already_exists
    ae_template, _ = EmailTemplate.objects.get_or_create(name='account_already_exists')
    ae_translations = {
        'ca': {
            'subject': 'Intent de registre amb un compte existent',
            'body': '<p>S\'ha rebut una petició de registre amb aquesta adreça electrònica: {{ email_addr }}</p><p>No obstant això, ja existeix un compte amb aquest correu. Per iniciar la sessió (Log in), pots sol·licitar un enllaç màgic a la pàgina d\'inici de sessió:</p><p><a href="{{ login_url }}">{{ login_url }}</a></p>',
            'plain_body': 'S\'ha rebut una petició de registre amb aquesta adreça electrònica: {{ email_addr }}\n\nNo obstant això, ja existeix un compte amb aquest correu. Per iniciar la sessió (Log in), pots sol·licitar un enllaç màgic a la pàgina d\'inici de sessió:\n{{ login_url }}'
        },
        'en': {
            'subject': 'Registration attempt with an existing account',
            'body': '<p>A registration request was received with this email address: {{ email_addr }}</p><p>However, an account already exists with this email. To log in, you can request a magic link on the login page:</p><p><a href="{{ login_url }}">{{ login_url }}</a></p>',
            'plain_body': 'A registration request was received with this email address: {{ email_addr }}\n\nHowever, an account already exists with this email. To log in, you can request a magic link on the login page:\n{{ login_url }}'
        },
        'es': {
            'subject': 'Intento de registro con una cuenta existente',
            'body': '<p>Se ha recibido una solicitud de registro con esta dirección de correo electrónico: {{ email_addr }}</p><p>Sin embargo, ya existe una cuenta con este correo. Para iniciar sesión, puedes solicitar un enlace mágico en la página de inicio de sesión:</p><p><a href="{{ login_url }}">{{ login_url }}</a></p>',
            'plain_body': 'Se ha recibido una solicitud de registro con esta dirección de correo electrónico: {{ email_addr }}\n\nSin embargo, ya existe una cuenta con este correo. Para iniciar sesión, puedes solicitar un enlace mágico en la página de inicio de sesión:\n{{ login_url }}'
        },
        'fr': {
            'subject': 'Tentative d\'inscription avec un compte existant',
            'body': '<p>Une demande d\'inscription a été reçue avec cette adresse e-mail : {{ email_addr }}</p><p>Cependant, un compte existe déjà avec cet e-mail. Pour vous connecter, vous pouvez demander un lien magique sur la page de connexion :</p><p><a href="{{ login_url }}">{{ login_url }}</a></p>',
            'plain_body': 'Une demande d\'inscription a été reçue avec cette adresse e-mail : {{ email_addr }}\n\nCependant, un compte existe déjà with cet e-mail. Pour vous connecter, vous pouvez demander un lien magique sur la page de connexion :\n{{ login_url }}'
        },
        'de': {
            'subject': 'Registrierungsversuch mit einem bestehenden Konto',
            'body': '<p>Eine Registrierungsanfrage mit dieser E-Mail-Adresse ist eingegangen: {{ email_addr }}</p><p>Es existiert jedoch bereits ein Konto mit dieser E-Mail. Um sich anzumelden, können Sie auf der Anmeldeseite einen Magic Link anfordern:</p><p><a href="{{ login_url }}">{{ login_url }}</a></p>',
            'plain_body': 'Eine Registrierungsanfrage mit dieser E-Mail-Adresse ist eingegangen: {{ email_addr }}\n\nEs existiert jedoch bereits ein Konto mit dieser E-Mail. Um sich anzumelden, können Sie auf der Anmeldeseite einen Magic Link anfordern:\n{{ login_url }}'
        },
        'it': {
            'subject': 'Tentativo di registrazione con un account esistente',
            'body': '<p>È stata ricevuta una richiesta di registrazione con questo indirizzo email: {{ email_addr }}</p><p>Tuttavia, esiste già un account con questa email. Per accedere, puoi richiedere un Magic Link nella pagina di login:</p><p><a href="{{ login_url }}">{{ login_url }}</a></p>',
            'plain_body': 'È stata ricevuta una richiesta di registrazione con questo indirizzo email: {{ email_addr }}\n\nTuttavia, esiste già un account con questa email. Per accedere, puoi richiedere un Magic Link nella pagina di login:\n{{ login_url }}'
        },
        'pt': {
            'subject': 'Tentativa de registro com uma conta existente',
            'body': '<p>Recebemos um pedido de registro com este endereço de e-mail: {{ email_addr }}</p><p>No entanto, já existe uma conta com este e-mail. Para fazer login, você pode solicitar um link mágico na página de login:</p><p><a href="{{ login_url }}">{{ login_url }}</a></p>',
            'plain_body': 'Recebemos um pedido de registro com este endereço de e-mail: {{ email_addr }}\n\nNo entanto, já existe uma conta com este e-mail. Para fazer login, você pode solicitar um link mágico na página de login:\n{{ login_url }}'
        }
    }
    for lang, data in ae_translations.items():
        EmailTemplateTranslation.objects.update_or_create(template=ae_template, language=lang, defaults=data)

def rollback_translations(apps, schema_editor):
    EmailTemplate = apps.get_model('post_office', 'EmailTemplate')
    EmailTemplate.objects.filter(name__in=['purchase_confirmation', 'login_code', 'account_already_exists']).delete()
    # For account_confirmation we might want to keep the original 3, but it's simpler to just leave it.

class Migration(migrations.Migration):
    dependencies = [
        ('post_office', '0004_seed_password_reset_template'),
    ]
    operations = [
        migrations.RunPython(complete_translations, rollback_translations),
    ]
