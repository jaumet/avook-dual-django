import polib
import os

def fix_po(lang):
    po_path = f'locale/{lang}/LC_MESSAGES/django.po'
    if not os.path.exists(po_path):
        return
    po = polib.pofile(po_path)

    translations = {
        "ca": {
            "You are receiving this email because user %(display_name)s has provided your email address to register an account at %(site_domain)s.":
            "Esteu rebent aquest correu electrònic perquè l'usuari %(display_name)s ha proporcionat la vostra adreça electrònica per registrar un compte a %(site_domain)s.",

            "Your email verification code is shown below. Please enter it in the open window of your browser.":
            "El vostre codi de verificació de correu electrònic es mostra a continuació. Introduïu-lo a la finestra oberta del vostre navegador.",

            "To confirm this is correct, go to %(activate_url)s":
            "Per confirmar que això és correcte, aneu a %(activate_url)s",

            "Your Magic Link for %(site_name)s":
            "El teu enllaç màgic per a %(site_name)s",

            "Confirmar dirección de correo electrónico":
            "Confirmar l'adreça de correu electrònic",

            "Dirección de correo electrónico confirmada":
            "Adreça de correu electrònic confirmada",

            "Ha confirmado correctamente su dirección de correo electrónico.":
            "Heu confirmat correctament la vostra adreça de correu electrònic.",

            "Confirmar":
            "Confirmar"
        },
        "es": {
            "You are receiving this email because user %(display_name)s has provided your email address to register an account at %(site_domain)s.":
            "Estás recibiendo este correo electrónico porque el usuario %(display_name)s ha proporcionado tu dirección de correo electrónico para registrar una cuenta en %(site_domain)s.",

            "Your email verification code is shown below. Please enter it in the open window of your browser.":
            "Tu código de verificación de correo electrónico se muestra a continuación. Por favor, introdúcelo en la ventana abierta de tu navegador.",

            "To confirm this is correct, go to %(activate_url)s":
            "Para confirmar que esto es correcto, ve a %(activate_url)s",

            "Your Magic Link for %(site_name)s":
            "Tu enlace mágico para %(site_name)s",

            "Verifique su dirección de correo electrónico":
            "Verifique su dirección de correo electrónico",

            "Le hemos enviado un correo electrónico para su verificación. Siga el enlace proporcionado para finalizar el proceso de registro. Si no ves el correo electrónico de verificación en tu bandeja de entrada principal, comprueba tu carpeta de correo no deseado. Por favor, póngase en contacto con nosotros si no recibe el correo electrónico de verificación en unos minutos.":
            "Le hemos enviado un correo electrónico para su verificación. Siga el enlace proporcionado para finalizar el proceso de registro. Si no ves el correo electrónico de verificación en tu bandeja de entrada principal, comprueba tu carpeta de correo no deseado. Por favor, póngase en contacto con nosotros si no recibe el correo electrónico de verificación en unos minutos.",

            "Confirmar dirección de correo electrónico":
            "Confirmar dirección de correo electrónico",

            "Por favor, confirme que <a href=\"mailto:%(confirmation)s\">%(confirmation)s</a> es la dirección de correo electrónico del usuario %(user_display)s.":
            "Por favor, confirme que <a href=\"mailto:%(confirmation)s\">%(confirmation)s</a> es la dirección de correo electrónico del usuario %(user_display)s.",

            "Este enlace de confirmación de correo electrónico ha caducado o no es válido. Por favor, <a href=\"%(email_url)s\">solicite una nueva confirmación de correo electrónico</a>.":
            "Este enlace de confirmación de correo electrónico ha caducado o no es válido. Por favor, <a href=\"%(email_url)s\">solicite una nueva confirmación de correo electrónico</a>.",

            "Dirección de correo electrónico confirmada":
            "Dirección de correo electrónico confirmada",

            "Ha confirmado correctamente su dirección de correo electrónico.":
            "Ha confirmado correctamente su dirección de correo electrónico.",

            "Iniciar sesión":
            "Iniciar sesión",

            "Confirmar":
            "Confirmar"
        }
    }

    for entry in po:
        if lang in translations and entry.msgid in translations[lang]:
            entry.msgstr = translations[lang][entry.msgid]
            if '%' in entry.msgid:
                if 'python-format' not in entry.flags:
                    entry.flags.append('python-format')

    po.save(po_path)

for l in ["ca", "es"]:
    fix_po(l)
print("PO files updated with more translations.")
