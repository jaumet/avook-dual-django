from django.contrib import admin
from .models import Product, Title, Package, UserPurchase, TitleLanguage


class TitleLanguageInline(admin.TabularInline):
    model = TitleLanguage
    extra = 1


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('human_name', 'levels', 'collection')
    search_fields = ('human_name', 'machine_name', 'collection')
    list_filter = ('levels', 'collection')
    prepopulated_fields = {'machine_name': ('human_name',)}
    inlines = [TitleLanguageInline]


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'level_range', 'is_free')
    search_fields = ('name', 'level_range')
    list_filter = ('level_range', 'is_free')
    filter_horizontal = ('titles',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'currency', 'is_free')
    search_fields = ('name', 'price')
    list_filter = ('is_free', 'currency')
    filter_horizontal = ('packages',)


@admin.register(UserPurchase)
class UserPurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'purchase_date')
    search_fields = ('user__username', 'product__name')
    list_filter = ('purchase_date',)
