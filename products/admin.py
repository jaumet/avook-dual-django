from django.contrib import admin
from django import forms
from django.urls import path
from django.shortcuts import render
from django.db.models import Sum, Count, Avg
from django.utils.translation import gettext_lazy as _
from .models import Product, Title, Package, UserPurchase, TranslatableContent, ProductTranslation, UserActivity, UserActivityStat

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


@admin.register(UserActivityStat)
class UserActivityStatAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'get_total_time', 'get_total_count', 'get_avg_completion')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('username', 'email', 'get_total_time', 'get_total_count', 'get_avg_completion')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            total_time=Sum('activities__listening_time'),
            total_count=Sum('activities__listen_count'),
            avg_completion=Avg('activities__completion_percentage')
        ).filter(total_count__gt=0)

    def get_total_time(self, obj):
        return obj.total_time
    get_total_time.short_description = _("Total Listening Time")
    get_total_time.admin_order_field = 'total_time'

    def get_total_count(self, obj):
        return obj.total_count
    get_total_count.short_description = _("Total Listen Count")
    get_total_count.admin_order_field = 'total_count'

    def get_avg_completion(self, obj):
        return f"{obj.avg_completion:.1f}%" if obj.avg_completion is not None else "0.0%"
    get_avg_completion.short_description = _("Avg. Completion")
    get_avg_completion.admin_order_field = 'avg_completion'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('statistics/', self.admin_site.admin_view(self.statistics_view), name='user-activity-statistics'),
        ]
        return custom_urls + urls

    def statistics_view(self, request):
        # Top 10 users by listening time
        top_users = UserActivity.objects.values('user__username', 'user__email').annotate(
            total_time=Sum('listening_time'),
            total_count=Sum('listen_count')
        ).order_by('-total_time')[:10]

        # Bottom 10 users by listening time (of those with activity)
        bottom_users = UserActivity.objects.values('user__username', 'user__email').annotate(
            total_time=Sum('listening_time'),
            total_count=Sum('listen_count')
        ).order_by('total_time')[:10]

        # Activity by language pair
        by_language = UserActivity.objects.values('language_pair').annotate(
            total_time=Sum('listening_time'),
            total_count=Sum('listen_count'),
            user_count=Count('user', distinct=True)
        ).order_by('-total_time')

        # Activity by level
        by_level = UserActivity.objects.values('title__level').annotate(
            total_time=Sum('listening_time'),
            total_count=Sum('listen_count'),
            user_count=Count('user', distinct=True)
        ).order_by('-total_time')

        context = dict(
            self.admin_site.each_context(request),
            top_users=top_users,
            bottom_users=bottom_users,
            by_language=by_language,
            by_level=by_level,
            title=_("User Activity Statistics"),
            opts=self.model._meta,
        )
        return render(request, 'admin/products/useractivity/statistics.html', context)


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'language_pair', 'listening_time', 'last_listened_date')
    list_filter = ('language_pair', 'title__level', 'last_listened_date')
    search_fields = ('user__username', 'user__email', 'title__machine_name')
    raw_id_fields = ('user', 'title')
