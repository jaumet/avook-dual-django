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
    class Meta:
        model = get_user_model()
        fields = ('username', 'email')
