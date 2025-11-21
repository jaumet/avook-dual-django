from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'language_pair', 'price', 'updated_at')
    search_fields = ('title', 'language_pair', 'level')
    list_filter = ('level', 'language_pair')
