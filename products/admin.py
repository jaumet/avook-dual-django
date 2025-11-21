from django.contrib import admin
from .models import Product, Title


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'language_pair', 'price', 'updated_at')
    search_fields = ('title', 'language_pair', 'level')
    list_filter = ('level', 'language_pair')
    filter_horizontal = ('titles',)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('title_human', 'level', 'languages', 'collection')
    search_fields = ('title_human', 'slug', 'collection', 'languages')
    list_filter = ('level', 'collection')
    prepopulated_fields = {'slug': ('title_human',)}
<<<<<<< ours

=======
>>>>>>> theirs
