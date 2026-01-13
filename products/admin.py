from django.contrib import admin
from django import forms
from .models import Product, Title, Package, UserPurchase, TranslatableContent, ProductTranslation

# Define the language choices for the dropdown
LANGUAGE_CHOICES = [
    ('ca', 'Català'),
    ('en', 'English'),
    ('es', 'Español'),
    ('fr', 'Français'),
    ('de', 'Deutsch'),
    ('it', 'Italiano'),
    ('pt', 'Português'),
]


class ProductTranslationForm(forms.ModelForm):
    language_code = forms.ChoiceField(choices=LANGUAGE_CHOICES)

    class Meta:
        model = ProductTranslation
        fields = ('language_code', 'name', 'description')


class ProductTranslationInline(admin.TabularInline):
    model = ProductTranslation
    form = ProductTranslationForm
    extra = 1


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('machine_name', 'level')
    search_fields = ('machine_name', 'level')
    list_filter = ('level',)


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'level')
    search_fields = ('name', 'level')
    list_filter = ('level',)
    filter_horizontal = ('titles',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductTranslationInline]
    list_display = ('get_name', 'machine_name', 'price', 'currency')
    search_fields = ('translations__name', 'machine_name', 'price')
    list_filter = ('currency',)
    filter_horizontal = ('packages',)
    fieldsets = (
        (None, {
            'fields': ('machine_name', 'price', 'currency', 'category', 'duration', 'packages')
        }),
    )

    def get_name(self, obj):
        translation = obj.get_translation()
        return translation.name if translation else 'No Name'
    get_name.short_description = 'Name'


@admin.register(UserPurchase)
class UserPurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_product_name', 'purchase_date', 'expiry_date')
    search_fields = ('user__username', 'product__translations__name')
    list_filter = ('purchase_date', 'expiry_date')
    raw_id_fields = ('user', 'product')

    def get_product_name(self, obj):
        translation = obj.product.get_translation()
        return translation.name if translation else 'N/A'
    get_product_name.short_description = 'Product'


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
