import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email_confirmed = models.BooleanField(default=False)
    confirmation_token = models.UUIDField(
        null=True,
        blank=True,
    )
    first_name = models.CharField("Nom", max_length=150, blank=False)
    last_name = models.CharField("Cognoms", max_length=150, blank=False)
    username = models.CharField(
        "Nom d'usuari",
        max_length=150,
        unique=True,
        help_text="Requerit. 150 caràcters o menys. Lletres, números i @/./+/-/_ només. sense espais.",
        validators=[AbstractUser.username_validator],
        error_messages={
            'unique': "Ja existeix un usuari amb aquest nom d'usuari.",
        },
    )
    email = models.EmailField('email address', blank=False)
    packages = models.ManyToManyField(
        'products.Package',
        verbose_name="paquets",
        blank=True,
        help_text="Els paquets als que aquest usuari té accés.",
        related_name="users",
    )
    known_languages = models.JSONField(
        "Llengües conegudes",
        default=list,
        blank=True,
        help_text="Llista de llengües que l'usuari coneix i el seu nivell."
    )
    learning_languages = models.JSONField(
        "Llengües a aprendre",
        default=list,
        blank=True,
        help_text="Llista de llengües que l'usuari vol aprendre i el seu nivell."
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Usuari"
        verbose_name_plural = "Usuaris"
