from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Title(models.Model):
    id = models.CharField(max_length=5, primary_key=True, help_text=_("ID del títol, p. ex., 10001"))
    machine_name = models.SlugField(unique=True, help_text=_("Nom intern sense espais, p. ex., 'el-meu-titol'"))
    human_name = models.CharField(max_length=255, help_text=_("Nom del títol per mostrar"))
    description = models.TextField(blank=True, help_text=_("Descripció del títol"))
    levels = models.CharField(max_length=50, blank=True, help_text=_("Nivells, p. ex., 'A2'"))
    langs = models.CharField(max_length=100, blank=True, help_text=_("Idiomes separats per comes, p. ex., 'CA, EN, FR'"))
    ages = models.CharField(max_length=20, blank=True, help_text=_("Rang d’edat, p. ex., '10-16'"))
    collection = models.CharField(max_length=100, blank=True, help_text=_("Col·lecció a la qual pertany"))
    duration = models.CharField(max_length=20, blank=True, help_text=_("Durada en format HH:MM:SS"))

    def __str__(self):
        return self.human_name

    class Meta:
        verbose_name = _("Títol")
        verbose_name_plural = _("Títols")


class Package(models.Model):
    id = models.CharField(max_length=5, primary_key=True, help_text=_("ID del paquet, p. ex., 20001"))
    name = models.CharField(max_length=255, help_text=_("Nom del paquet"))
    level_range = models.CharField(max_length=50, blank=True, help_text=_("Rang de nivells del paquet, p. ex., 'A0'"))
    description = models.TextField(blank=True, help_text=_("Descripció del paquet"))
    is_free = models.BooleanField(default=False, help_text=_("És un paquet gratuït?"))
    titles = models.ManyToManyField(Title, related_name='packages', help_text=_("Títols inclosos en aquest paquet"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Paquet")
        verbose_name_plural = _("Paquets")


class Product(models.Model):
    id = models.CharField(max_length=5, primary_key=True, help_text=_("ID del producte, p. ex., 30001"))
    name = models.CharField(max_length=255, help_text=_("Nom del producte"))
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text=_("Preu del producte"))
    currency = models.CharField(max_length=10, default='euro', help_text=_("Moneda del preu"))
    description = models.TextField(blank=True, help_text=_("Descripció del producte"))
    is_free = models.BooleanField(default=False, help_text=_("És un producte gratuït?"))
    packages = models.ManyToManyField(Package, related_name='products', help_text=_("Paquets inclosos en aquest producte"))

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
        verbose_name = _("Producte")
        verbose_name_plural = _("Productes")


class UserPurchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchases')
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

    class Meta:
        unique_together = ('user', 'product')
        verbose_name = _("Compra d'usuari")
        verbose_name_plural = _("Compres d'usuaris")
