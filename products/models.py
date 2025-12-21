import os
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.templatetags.static import static
from django_ckeditor_5.fields import CKEditor5Field


class Title(models.Model):
    id = models.AutoField(primary_key=True)
    machine_name = models.SlugField(unique=True, help_text="Nom intern sense espais, p. ex., 'el-meu-titol'")
    description = models.TextField(blank=True, help_text="Descripció del títol")
    levels = models.CharField(max_length=50, blank=True, help_text="Nivells, p. ex., 'A2'")
    ages = models.CharField(max_length=20, blank=True, help_text="Rang d’edat, p. ex., '10-16'")
    collection = models.CharField(max_length=100, blank=True, help_text="Col·lecció a la qual pertany")
    duration = models.CharField(max_length=20, blank=True, help_text="Durada en format HH:MM:SS")

    def __str__(self):
        return self.machine_name

    def get_image_url(self):
        image_path = f"AUDIOS/{self.machine_name}/{self.machine_name}.png"
        image_fullpath = os.path.join(settings.STATICFILES_DIRS[0], image_path)

        if os.path.exists(image_fullpath):
            return static(image_path)
        else:
            return static("imgs/anonymous-cover.png")

    def get_user_status(self, user):
        """
        Determina l'estat del títol per a un usuari específic.
        Retorna 'FREE', 'PREMIUM_OWNED', o 'PREMIUM_NOT_OWNED'.
        """
        if self.packages.filter(is_free=True).exists():
            return 'FREE'

        if user and user.is_authenticated:
            # This is an optimized query to check for access.
            # It avoids N+1 queries by performing a single DB lookup.
            is_owned = UserPurchase.objects.filter(
                user=user,
                product__packages__titles=self
            ).filter(
                Q(expiry_date__gte=timezone.now()) | Q(expiry_date__isnull=True)
            ).exists()

            if is_owned:
                return 'PREMIUM_OWNED'

        return 'PREMIUM_NOT_OWNED'

    class Meta:
        verbose_name = "Títol"
        verbose_name_plural = "Títols"


class TitleLanguage(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='languages')
    language = models.CharField(max_length=2, help_text="Codi de l'idioma, p. ex., 'CA'")
    human_name = models.CharField(max_length=255, help_text="Nom del títol per mostrar en l'idioma especificat")
    directory = models.CharField(max_length=255, help_text="Ruta al directori de l'idioma")
    json_file = models.CharField(max_length=255, help_text="Nom del fitxer JSON de l'idioma")

    def __str__(self):
        return f"{self.human_name} ({self.language})"

    class Meta:
        unique_together = ('title', 'language')
        verbose_name = "Ruta d'idioma del títol"
        verbose_name_plural = "Rutes d'idioma del títol"


class Package(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, help_text="Nom del paquet")
    level_range = models.CharField(max_length=50, blank=True, help_text="Rang de nivells del paquet, p. ex., 'A0'")
    description = models.TextField(blank=True, help_text="Descripció del paquet")
    is_free = models.BooleanField(default=False, help_text="És un paquet gratuït?")
    is_default_free = models.BooleanField(default=False, help_text="Marca si aquest és el paquet gratuït per defecte per a nous usuaris")
    titles = models.ManyToManyField(Title, related_name='packages', help_text="Títols inclosos en aquest paquet")

    def __str__(self):
        return self.name

    def clean(self):
        if self.is_default_free:
            if Package.objects.filter(is_default_free=True).exclude(pk=self.pk).exists():
                raise models.ValidationError("Ja existeix un paquet gratuït per defecte.")
    class Meta:
        verbose_name = "Paquet"
        verbose_name_plural = "Paquets"


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, help_text="Nom del producte")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Preu del producte")
    currency = models.CharField(max_length=10, default='euro', help_text="Moneda del preu")
    description = models.TextField(blank=True, help_text="Descripció del producte")
    is_free = models.BooleanField(default=False, help_text="És un producte gratuït?")
    packages = models.ManyToManyField(Package, related_name='products', help_text="Paquets inclosos en aquest producte")
    duration = models.IntegerField(default=0, help_text="Durada del producte en mesos")
    category = models.CharField(max_length=50, blank=True, help_text="Categoria del producte")

    def __str__(self):
        return self.name

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


class UserPurchase(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchases')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchases')
    purchase_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.expiry_date and self.product.duration:
            self.expiry_date = timezone.now() + relativedelta(months=self.product.duration)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

    class Meta:
        unique_together = ('user', 'product')
        verbose_name = "Compra d'usuari"
        verbose_name_plural = "Compres d'usuaris"


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
