from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'language_pair', 'price', 'updated_at')
    search_fields = ('title', 'language_pair')
    list_filter = ('language_pair',)
