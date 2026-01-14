from django import forms
from django.utils.translation import gettext_lazy as _
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
