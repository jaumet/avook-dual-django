from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

class ChatSession(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='chat_sessions')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat session for {self.user.username} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role.capitalize()} message in session {self.session.id} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
