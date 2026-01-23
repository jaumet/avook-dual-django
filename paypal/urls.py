from django.urls import path
from .views import paypal_webhook, get_payment_link_view

app_name = 'paypal'

urlpatterns = [
    path('webhook/', paypal_webhook, name='webhook'),
    path('create-link/<int:product_id>/', get_payment_link_view, name='create_payment_link'),
]
