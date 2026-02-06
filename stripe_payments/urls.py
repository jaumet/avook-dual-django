from django.urls import path
from .views import create_checkout_session, stripe_webhook

app_name = 'stripe_payments'

urlpatterns = [
    path('create-checkout-session/', create_checkout_session, name='create_checkout_session'),
    path('webhook/', stripe_webhook, name='webhook'),
]
