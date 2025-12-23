from django.contrib import admin
from .models import EmailTemplate, EmailTemplateTranslation

class EmailTemplateTranslationInline(admin.TabularInline):
    model = EmailTemplateTranslation
    extra = 1

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [EmailTemplateTranslationInline]
