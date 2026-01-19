from django.urls import path
from .views import paypal_webhook

app_name = 'paypal'

urlpatterns = [
    path('webhook/', paypal_webhook, name='webhook'),
]
