import polib
import os

translations = {
    "ca": {
        "Sign Up": "Crea un compte",
        "Log in if you already have an account": "Iniciar sessió si ja tens usuari",
        "Verify Your Email Address": "Verifica la teva adreça de correu",
        "Verification Email Sent": "Verificació de correu enviada",
        "Confirm Email Address": "Confirmar correu electrònic",
        "Account Inactive": "Compte inactiu",
        "Please Confirm Your Email Address": "Confirma la teva adreça electrònica",
        "Hello from {{ site_name }}!": "Hola des de {{ site_name }}!",
        "Thank you for using {{ site_name }}!": "Gràcies per utilitzar {{ site_name }}!",
        "Username": "Nom d'usuari",
        "You are receiving this email because user {{ display_name }} has provided your email address to register an account at {{ site_domain }}.": "Esteu rebent aquest correu electrònic perquè l'usuari {{ display_name }} ha proporcionat la vostra adreça electrònica per registrar un compte a {{ site_domain }}."
    },
    "es": {
        "Sign Up": "Crear cuenta",
        "Log in if you already have an account": "Iniciar sesión si ya tienes cuenta",
        "Verify Your Email Address": "Verifique su dirección de correo electrónico",
        "Verification Email Sent": "Correo electrónico de verificación enviado",
        "Confirm Email Address": "Confirmar dirección de correo electrónico",
        "Account Inactive": "Cuenta inactiva",
        "Please Confirm Your Email Address": "Por favor confirme su dirección de correo electrónico",
        "Hello from {{ site_name }}!": "Hola desde {{ site_name }}!",
        "Thank you for using {{ site_name }}!": "¡Gracias por usar {{ site_name }}!",
        "Username": "Nombre de usuario",
        "You are receiving this email because user {{ display_name }} has provided your email address to register an account at {{ site_domain }}.": "Está recibiendo este correo electrónico porque el usuario {{ display_name }} ha proporcionado su dirección de correo electrónico para registrar una cuenta en {{ site_domain }}."
    },
    "pt": {
        "Sign Up": "Criar conta",
        "Log in if you already have an account": "Faça login se você já tem uma conta",
        "Verify Your Email Address": "Verifique o seu endereço de e-mail",
        "Verification Email Sent": "E-mail de verificação enviado",
        "Confirm Email Address": "Confirmar endereço de e-mail",
        "Account Inactive": "Conta inativa",
        "Please Confirm Your Email Address": "Por favor confirme o seu endereço de e-mail",
        "Hello from {{ site_name }}!": "Olá de {{ site_name }}!",
        "Thank you for using {{ site_name }}!": "Obrigado por usar {{ site_name }}!",
        "Username": "Nome de usuário",
        "You are receiving this email because user {{ display_name }} has provided your email address to register an account at {{ site_domain }}.": "Está a receber este e-mail porque o utilizador {{ display_name }} forneceu o seu endereço de e-mail para registar uma conta em {{ site_domain }}."
    }
}

for lang, items in translations.items():
    po_path = f'locale/{lang}/LC_MESSAGES/django.po'
    if os.path.exists(po_path):
        po = polib.pofile(po_path)
        for msgid, msgstr in items.items():
            entry = po.find(msgid)
            if entry:
                entry.msgstr = msgstr
                if 'fuzzy' in entry.flags:
                    entry.flags.remove('fuzzy')
            else:
                po.append(polib.POEntry(
                    msgid=msgid,
                    msgstr=msgstr
                ))
        po.save()
        print(f"Updated {po_path}")
