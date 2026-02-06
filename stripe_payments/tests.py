import json
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, Mock
from products.models import Product, UserPurchase, UserAccess
from accounts.models import CustomUser
from django.utils import timezone

class StripeWebhookTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='stripeuser', email='stripeuser@example.com', pk=456)
        self.product = Product.objects.create(machine_name='stripe-product', price=15.00, stripe_price_id='price_123')
        self.webhook_url = reverse('stripe_payments:webhook')

    @patch('stripe.Webhook.construct_event')
    @patch('products.services.send_purchase_confirmation_email')
    def test_webhook_checkout_session_completed(self, mock_send_email, mock_construct_event):
        # Mock Stripe event
        mock_construct_event.return_value = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'cs_test_123',
                    'metadata': {
                        'user_id': str(self.user.id),
                        'product_id': str(self.product.id)
                    }
                }
            }
        }

        response = self.client.post(
            self.webhook_url,
            data=json.dumps({'dummy': 'data'}),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='dummy_sig'
        )

        self.assertEqual(response.status_code, 200)

        # Verify UserPurchase
        purchase = UserPurchase.objects.get(user=self.user, product=self.product)
        self.assertEqual(purchase.stripe_checkout_id, 'cs_test_123')
        self.assertEqual(purchase.payment_provider, 'stripe')
        self.assertEqual(purchase.status, 'completed')

        # Verify UserAccess
        access = UserAccess.objects.get(user=self.user, product=self.product)
        self.assertTrue(access.active)

        # Verify email was called
        mock_send_email.assert_called_once()

class StripeSessionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='stripeuser2', email='stripeuser2@example.com', password='password', pk=457)
        self.product = Product.objects.create(machine_name='stripe-product-2', price=20.00, stripe_price_id='price_456')
        self.client.login(username='stripeuser2', password='password')

    @patch('stripe.checkout.Session.create')
    def test_create_checkout_session(self, mock_session_create):
        mock_session_create.return_value = Mock(url='https://stripe.com/checkout/session/123')

        url = reverse('stripe_payments:create_checkout_session')
        response = self.client.post(
            url,
            data=json.dumps({'product_id': self.product.id}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['url'], 'https://stripe.com/checkout/session/123')
        mock_session_create.assert_called_once()
