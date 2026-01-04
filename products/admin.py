from django.contrib import admin
from .models import Product, Title, Package, UserPurchase, TitleLanguage, TranslatableContent, ProductTranslation


class ProductTranslationInline(admin.TabularInline):
    model = ProductTranslation
    extra = 1


class TitleLanguageInline(admin.TabularInline):
    model = TitleLanguage
    extra = 1


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('machine_name', 'levels', 'collection')
    search_fields = ('machine_name', 'collection')
    list_filter = ('levels', 'collection')
    inlines = [TitleLanguageInline]


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'level_range', 'is_free')
    search_fields = ('name', 'level_range')
    list_filter = ('level_range', 'is_free')
    filter_horizontal = ('titles',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductTranslationInline]
    list_display = ('get_name', 'price', 'currency', 'is_free')
    search_fields = ('translations__name', 'price')
    list_filter = ('is_free', 'currency')
    filter_horizontal = ('packages',)

    def get_name(self, obj):
        translation = obj.get_translation()
        return translation.name if translation else 'No Name'
    get_name.short_description = 'Name'


@admin.register(UserPurchase)
class UserPurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'purchase_date')
    search_fields = ('user__username', 'product__name')
    list_filter = ('purchase_date',)


from .models import HomePageContent

@admin.register(TranslatableContent)
class TranslatableContentAdmin(admin.ModelAdmin):
    list_display = ('key',)
    search_fields = ('key',)

    class Media:
        css = {
            'all': ('css/custom_ckeditor.css',)
        }

@admin.register(HomePageContent)
class HomePageContentAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        # Prevent adding new instances if one already exists
        return not HomePageContent.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deleting the singleton instance
        return False
