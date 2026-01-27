import uuid
from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    email_confirmed = models.BooleanField(default=False)
    is_first_login = models.BooleanField(default=True)
    confirmation_token = models.UUIDField(
        null=True,
        blank=True,
    )
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Minimum 5 characters. Only letters and numbers.'),
        validators=[
            validators.RegexValidator(
                r'^[a-zA-Z0-9]+$',
                _('Enter a valid username. This value may contain only letters and numbers.'),
            ),
            validators.MinLengthValidator(5, _('Username must be at least 5 characters long.')),
        ],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(
        _('email address'),
        unique=True,
        blank=False,
        help_text=_('Unique email address.'),
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
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
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        constraints = [
            models.UniqueConstraint(
                Lower('username'),
                name='unique_username_case_insensitive'
            ),
            models.UniqueConstraint(
                Lower('email'),
                name='unique_email_case_insensitive'
            ),
        ]
