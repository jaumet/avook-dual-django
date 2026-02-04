import os
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import models
from django.db.models import Q
import datetime
from django.utils import timezone
from django.utils.translation import get_language, gettext_lazy as _
from django.templatetags.static import static
from django_ckeditor_5.fields import CKEditor5Field
from accounts.models import CustomUser


class Title(models.Model):
    id = models.AutoField(primary_key=True)
    machine_name = models.SlugField(unique=True, help_text="Nom intern sense espais, p. ex., 'el-meu-titol'")
    level = models.CharField(max_length=50, blank=True, help_text="Nivell, p. ex., 'A2'")

    def __str__(self):
        return self.machine_name

    def get_image_url(self):
        image_filename = f"{self.machine_name}.png"
        image_relative_path = f"{self.level}/{self.machine_name}/{image_filename}"

        # Check if it exists in AUDIOS_ROOT
        image_fullpath = os.path.join(settings.AUDIOS_ROOT, image_relative_path)

        if os.path.exists(image_fullpath):
            return f"{settings.AUDIOS_URL}{image_relative_path}"

        # Fallback to default images in STATIC
        default_image_path = f"imgs/{self.level}-anonymous-cover.png"
        default_image_fullpath = os.path.join(settings.STATICFILES_DIRS[0], default_image_path)

        if os.path.exists(default_image_fullpath):
            return static(default_image_path)

        return static("imgs/anonymous-cover.png")

    def get_user_status(self, user):
        """
        Determina l'estat del títol per a un usuari específic.
        Retorna 'PREMIUM_OWNED', o 'PREMIUM_NOT_OWNED'.
        """
        # Grant access if the title is part of any free product.
        if Product.objects.filter(price=0, packages__titles=self).exists():
            return 'PREMIUM_OWNED'

        if user and user.is_authenticated:
            # Grant access to staff/admin users immediately
            if user.is_staff:
                return 'PREMIUM_OWNED'

            # Check UserAccess (new system)
            is_owned = UserAccess.objects.filter(
                Q(expiry_date__gte=timezone.now()) | Q(expiry_date__isnull=True),
                user=user,
                product__packages__titles=self,
                active=True
            ).exists()

            if is_owned:
                return 'PREMIUM_OWNED'

            # Fallback for legacy UserPurchase records (migration period)
            is_owned_legacy = UserPurchase.objects.filter(
                user=user,
                product__packages__titles=self,
                expiry_date__gte=timezone.now()
            ).exists()

            if is_owned_legacy:
                return 'PREMIUM_OWNED'

        return 'PREMIUM_NOT_OWNED'

    class Meta:
        verbose_name = "Títol"
        verbose_name_plural = "Títols"


class TitleTranslation(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='translations')
    language_code = models.CharField(max_length=10)
    human_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('title', 'language_code')
        verbose_name = "Traducció de Títol"
        verbose_name_plural = "Traduccions de Títol"

    def __str__(self):
        return f"{self.human_name} ({self.language_code})"


class Package(models.Model):
    LEVEL_CHOICES = [
        ('A0', 'A0'),
        ('A1', 'A1'),
        ('A2', 'A2'),
        ('B1', 'B1'),
        ('B2', 'B2'),
        ('C1', 'C1'),
    ]
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, help_text="Nom del paquet")
    level = models.CharField(
        max_length=2,
        choices=LEVEL_CHOICES,
        help_text="Nivell del paquet"
    )
    titles = models.ManyToManyField(Title, related_name='packages', help_text="Títols inclosos en aquest paquet")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Paquet"
        verbose_name_plural = "Paquets"


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    machine_name = models.SlugField(unique=True, help_text="Nom intern sense espais, p. ex., 'el-meu-producte'", blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Preu del producte")
    currency = models.CharField(max_length=10, default='euro', help_text="Moneda del preu")
    packages = models.ManyToManyField(Package, related_name='products', help_text="Paquets inclosos en aquest producte")
    duration = models.IntegerField(default=0, help_text="Durada del producte en mesos")
    category = models.CharField(max_length=50, blank=True, help_text="Categoria del producte")

    def __str__(self):
        translation = self.get_translation()
        if translation:
            return translation.name
        return self.machine_name or f"Product {self.pk}"

    def get_translation(self, language_code=None):
        if not language_code:
            language_code = get_language()

        # Ensure language_code is not None and is lowercased for case-insensitive matching.
        language_code = (language_code or '').lower()

        if hasattr(self, '_prefetched_objects_cache') and 'translations' in self._prefetched_objects_cache:
            translations = self._prefetched_objects_cache['translations']
        else:
            translations = self.translations.all()

        if not translations:
            return None  # Return None if no translations exist at all

        # Create a dictionary with lowercased language codes for case-insensitive lookup.
        trans_dict = {t.language_code.lower(): t for t in translations}

        # 1. Try to get the requested language
        translation = trans_dict.get(language_code)
        if translation:
            return translation

        # 2. Fallback to the primary language part (e.g., 'en' from 'en-us')
        if '-' in language_code:
            primary_language_code = language_code.split('-')[0]
            translation = trans_dict.get(primary_language_code)
            if translation:
                return translation

        # 3. Fallback to the default language from settings (lowercased)
        translation = trans_dict.get(settings.LANGUAGE_CODE.lower())
        if translation:
            return translation

        # 4. Fallback to English 'en' if it exists
        translation = trans_dict.get('en')
        if translation:
            return translation

        # 5. Fallback to the first available translation
        return list(translations)[0]


    @property
    def title_ids(self):
        """ Retorna una llista plana de tots els machine_name dels títols d'aquest producte. """
        title_ids_set = set()
        for package in self.packages.all():
            for title in package.titles.all():
                title_ids_set.add(title.machine_name)
        return list(title_ids_set)

    class Meta:
        verbose_name = "Producte"
        verbose_name_plural = "Productes"


class ProductTranslation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='translations')
    language_code = models.CharField(max_length=10)
    name = models.CharField(max_length=255)
    description = CKEditor5Field('Description', blank=True)

    class Meta:
        unique_together = ('product', 'language_code')
        verbose_name = "Traducció de Producte"
        verbose_name_plural = "Traduccions de Producte"

    def __str__(self):
        return f"{self.name} ({self.language_code})"


class UserPurchase(models.Model):
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchases')
    user_email = models.EmailField(max_length=255, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchases')
    purchase_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    paypal_order_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    paypal_capture_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_provider = models.CharField(max_length=50, default='paypal')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')

    def save(self, *args, **kwargs):
        if not self.expiry_date and self.product.duration:
            # For paid_at or purchase_date
            base_date = self.paid_at or timezone.now()
            self.expiry_date = base_date + relativedelta(months=self.product.duration)
        super().save(*args, **kwargs)

    def __str__(self):
        product_name = f"Product {self.product.pk}"
        if self.product:
            translation = self.product.get_translation()
            if translation and hasattr(translation, 'name'):
                product_name = translation.name
            elif self.product.machine_name:
                product_name = self.product.machine_name

        return f"{self.user.username} - {product_name} ({self.status})"

    class Meta:
        verbose_name = "Compra d'usuari"
        verbose_name_plural = "Compres d'usuaris"


class UserAccess(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='accesses')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='accesses')
    active = models.BooleanField(default=True)
    activated_at = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.machine_name} (Active: {self.active})"

    class Meta:
        unique_together = ('user', 'product')
        verbose_name = "Accés d'usuari"
        verbose_name_plural = "Accessos d'usuaris"


class TranslatableContent(models.Model):
    key = models.CharField(max_length=100, unique=True, help_text="Clau única per identificar el contingut, p. ex., 'home_page_main_content'")
    content_ca = CKEditor5Field('Contingut (Català)', blank=True)
    content_en = CKEditor5Field('Contingut (English)', blank=True)
    content_es = CKEditor5Field('Contingut (Español)', blank=True)
    content_fr = CKEditor5Field('Contingut (Français)', blank=True)
    content_pt = CKEditor5Field('Contingut (Português)', blank=True)
    content_de = CKEditor5Field('Contingut (Deutsch)', blank=True)
    content_it = CKEditor5Field('Contingut (Italiano)', blank=True)

    def __str__(self):
        return self.key

    class Meta:
        verbose_name = "Contingut Traduïble"
        verbose_name_plural = "Continguts Traduïbles"


class HomePageContent(models.Model):
    content_ca = models.TextField(verbose_name='Home-Page_Content (Català)', blank=True)
    content_en = models.TextField(verbose_name='Home-Page_Content (English)', blank=True)
    content_es = models.TextField(verbose_name='Home-Page_Content (Español)', blank=True)
    content_fr = models.TextField(verbose_name='Home-Page_Content (Français)', blank=True)
    content_pt = models.TextField(verbose_name='Home-Page_Content (Português)', blank=True)
    content_de = models.TextField(verbose_name='Home-Page_Content (Deutsch)', blank=True)
    content_it = models.TextField(verbose_name='Home-Page_Content (Italiano)', blank=True)

    def __str__(self):
        return "Homepage Content"

    class Meta:
        verbose_name = "Homepage Content"
        verbose_name_plural = "Homepage Content"


class UserActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities')
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='activities')
    language_pair = models.CharField(max_length=10, help_text="e.g., 'en-es'")
    listening_time = models.DurationField(default=datetime.timedelta(0))
    completion_percentage = models.FloatField(default=0.0)
    listen_count = models.PositiveIntegerField(default=0)
    last_listened_date = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.title.machine_name} ({self.language_pair})"

    class Meta:
        verbose_name = _("Activity Log")
        verbose_name_plural = _("Activity Logs")
        unique_together = ('user', 'title', 'language_pair')


class UserActivityStat(CustomUser):
    class Meta:
        proxy = True
        verbose_name = _('User Activity (Accumulated)')
        verbose_name_plural = _('User Activities (Accumulated)')
