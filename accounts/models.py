import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    email_confirmed = models.BooleanField(default=False)
    confirmation_token = models.UUIDField(
        null=True,
        blank=True,
    )
    first_name = models.CharField(_('first name'), max_length=150, blank=False)
    last_name = models.CharField(_('last name'), max_length=150, blank=False)
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[AbstractUser.username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_('email address'), blank=False)
    known_languages = models.JSONField(
        _('known languages'),
        default=list,
        blank=True,
        help_text=_('A list of languages the user knows and their level.')
    )
    learning_languages = models.JSONField(
        _('learning languages'),
        default=list,
        blank=True,
        help_text=_('A list of languages the user wants to learn and their level.')
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
