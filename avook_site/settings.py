import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'insecure-secret-key-change-me')
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django_ckeditor_5',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'products',
    'accounts',
    'post_office',
    'paypal',
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'avook_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates', BASE_DIR / 'accounts' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'avook_site.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGES = [
    ('ca', _('Catalan')),
    ('en', _('English')),
    ('es', _('Spanish')),
    ('fr', _('French')),
    ('de', _('German')),
    ('it', _('Italian')),
    ('pt', _('Portuguese')),
]

LANGUAGE_CODE = 'ca'

TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'
AUTH_USER_MODEL = 'accounts.CustomUser'

CKEDITOR_5_UPLOAD_PATH = "uploads/"

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'blockQuote'],
    },
    'richtext-minimal': {
        'toolbar': ['bold', 'italic', 'link'],
        'language': 'ca',
    }
}

## Preparing the API_KEY varriable
from pathlib import Path
import os
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

RESEND_API_KEY = os.environ["RESEND_API_KEY"]
DEFAULT_FROM_EMAIL = "Dual <no-reply@dual.cat>"

# --- PayPal Configuration Selector ---
PAYPAL_MODE = os.environ.get('PAYPAL_MODE')

if PAYPAL_MODE == 'sandbox':
    PAYPAL_API_URL = os.environ.get('PAYPAL_API_URL_SANDBOX')
    PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID_SANDBOX')
    PAYPAL_SECRET = os.environ.get('PAYPAL_SECRET_SANDBOX')
    PAYPAL_WEBHOOK_ID = os.environ.get('PAYPAL_WEBHOOK_ID_SANDBOX')
elif PAYPAL_MODE == 'live':
    PAYPAL_API_URL = os.environ.get('PAYPAL_API_URL_LIVE')
    PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID_LIVE')
    PAYPAL_SECRET = os.environ.get('PAYPAL_SECRET_LIVE')
    PAYPAL_WEBHOOK_ID = os.environ.get('PAYPAL_WEBHOOK_ID_LIVE')
else:
    raise ImproperlyConfigured(
        f"PAYPAL_MODE té un valor invàlid: '{PAYPAL_MODE}'. Ha de ser 'sandbox' o 'live'."
    )

# Validació de les credencials carregades
if not all([PAYPAL_API_URL, PAYPAL_CLIENT_ID, PAYPAL_SECRET, PAYPAL_WEBHOOK_ID]):
    raise ImproperlyConfigured(
        f"Falten credencials de PayPal per al mode '{PAYPAL_MODE}'. "
        "Assegura't que totes les variables PAYPAL_* estiguin definides al fitxer .env."
    )
# --- End of PayPal Configuration ---
