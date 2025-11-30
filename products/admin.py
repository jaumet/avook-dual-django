from django.contrib import admin
from .models import Product, Title, Package, UserPurchase, TitleLanguage, TranslatableContent


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
