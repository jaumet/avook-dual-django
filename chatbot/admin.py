from django.contrib import admin
from .models import ChatSession, ChatMessage

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('role', 'content', 'created_at')
    can_delete = False

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username',)
    inlines = [ChatMessageInline]
    readonly_fields = ('user', 'created_at')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'role', 'content_snippet', 'created_at')
    list_filter = ('created_at', 'role')
    search_fields = ('content', 'session__user__username')
    readonly_fields = ('session', 'role', 'content', 'created_at')

    def content_snippet(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_snippet.short_description = 'Content'
