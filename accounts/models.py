from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    first_name = models.CharField(_("Nom"), max_length=150, blank=False)
    last_name = models.CharField(_("Cognoms"), max_length=150, blank=False)
    username = models.CharField(
        _("Nom d'usuari"),
        max_length=150,
        unique=True,
        help_text=_("Requerit. 150 caràcters o menys. Lletres, números i @/./+/-/_ només. sense espais."),
        validators=[AbstractUser.username_validator],
        error_messages={
            'unique': _("Ja existeix un usuari amb aquest nom d'usuari."),
        },
    )
    email = models.EmailField(_('email address'), blank=False)
    packages = models.ManyToManyField(
        'products.Package',
        verbose_name=_("paquets"),
        blank=True,
        help_text=_("Els paquets als que aquest usuari té accés."),
        related_name="users",
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = _("Usuari")
        verbose_name_plural = _("Usuaris")
