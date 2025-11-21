from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
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
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
