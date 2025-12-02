import uuid
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Product, Title, TitleLanguage


class TitleForm(forms.ModelForm):
    class Meta:
        model = Title
        fields = [
            'id',
            'machine_name',
            'human_name',
            'description',
            'levels',
            'ages',
            'collection',
            'duration',
        ]


class TitleLanguageForm(forms.ModelForm):
    class Meta:
        model = TitleLanguage
        fields = ['language', 'directory', 'json_file']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'price',
            'currency',
            'description',
            'is_free',
            'packages',
        ]


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Nom.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Cognoms.')
    email = forms.EmailField(max_length=254, required=True, help_text='Correu electrònic.')

    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False  # Deactivate account until email confirmation
        user.is_staff = False
        user.is_superuser = False
        user.confirmation_token = uuid.uuid4()
        if commit:
            user.save()
        return user
