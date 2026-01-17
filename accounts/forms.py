import json
import uuid

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    PasswordResetForm,
    UserChangeForm,
    UserCreationForm,
)
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from post_office.utils import send_templated_email

from .models import CustomUser

User = get_user_model()


# Form for Admin to CREATE a user
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name')


# Form for Admin to CHANGE a user
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'known_languages', 'learning_languages')


# Form for public user SIGNUP
class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label=_('First name'))
    last_name = forms.CharField(max_length=30, required=True, label=_('Last name'))
    email = forms.EmailField(max_length=254, required=True, label=_('Email'))

    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email')
        labels = {
            'username': _('Username'),
        }

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['password2'].label = _("Password confirmation")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False
        user.is_staff = False
        user.is_superuser = False
        user.confirmation_token = str(uuid.uuid4())
        if commit:
            user.save()
        return user


# Form for user-facing PROFILE UPDATE
class ProfileUpdateForm(forms.ModelForm):
    known_languages = forms.CharField(widget=forms.HiddenInput(), required=False)
    learning_languages = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'known_languages', 'learning_languages']
        labels = {
            'first_name': _('First name'),
            'last_name': _('Last name'),
            'email': _('Email'),
        }

    def clean_known_languages(self):
        languages = self.cleaned_data.get('known_languages')
        if languages:
            try:
                return json.loads(languages)
            except json.JSONDecodeError:
                raise forms.ValidationError("Invalid JSON format for known languages.")
        return []

    def clean_learning_languages(self):
        languages = self.cleaned_data.get('learning_languages')
        if languages:
            try:
                return json.loads(languages)
            except json.JSONDecodeError:
                raise forms.ValidationError("Invalid JSON format for learning languages.")
        return []

# Form for public user PASSWORD RESET
class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        path = reverse(
            "accounts:password_reset_confirm",
            kwargs={"uidb64": context["uid"], "token": context["token"]},
        )

        custom_context = context.copy()
        custom_context['path'] = path

        send_templated_email(
            template_name="password_reset",
            context=custom_context,
            to_email=to_email,
        )
