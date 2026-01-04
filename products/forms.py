import uuid
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from .models import Product, Title


class TitleForm(forms.ModelForm):
    class Meta:
        model = Title
        fields = [
            'id',
            'machine_name',
            'level',
        ]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'id',
            'price',
            'currency',
            'packages',
        ]


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
        user.confirmation_token = uuid.uuid4()
        if commit:
            user.save()
        return user
