import json
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from products.models import Product, UserPurchase
from django.contrib.auth import get_user_model

User = get_user_model()

class PayPalWebhookTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', pk=123)
        self.product = Product.objects.create(machine_name='test-product', price=10.00)
        self.webhook_url = reverse('paypal:webhook')

    @patch('paypal.views.verify_paypal_signature')
    def test_webhook_payment_capture_completed(self, mock_verify):
        mock_verify.return_value = True

        payload = {
            "event_type": "PAYMENT.CAPTURE.COMPLETED",
            "resource": {
                "custom_id": "123",
                "purchase_units": [
                    {
                        "items": [
                            {
                                "sku": "test-product"
                            }
                        ]
                    }
                ]
            }
        }

        response = self.client.post(
            self.webhook_url,
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_PAYPAL_AUTH_ALGO='algo',
            HTTP_PAYPAL_CERT_URL='url',
            HTTP_PAYPAL_TRANSMISSION_ID='id',
            HTTP_PAYPAL_TRANSMISSION_SIG='sig',
            HTTP_PAYPAL_TRANSMISSION_TIME='time'
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(UserPurchase.objects.filter(user=self.user, product=self.product).exists())

    @patch('paypal.views.verify_paypal_signature')
    def test_webhook_encoded_sku(self, mock_verify):
        mock_verify.return_value = True

        # User ID 456, Product 'test-product'
        user = User.objects.create_user(username='testuser2', pk=456)

        payload = {
            "event_type": "PAYMENT.CAPTURE.COMPLETED",
            "resource": {
                "purchase_units": [
                    {
                        "items": [
                            {
                                "sku": "test-product:456"
                            }
                        ]
                    }
                ]
            }
        }

        response = self.client.post(
            self.webhook_url,
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_PAYPAL_AUTH_ALGO='algo',
            HTTP_PAYPAL_CERT_URL='url',
            HTTP_PAYPAL_TRANSMISSION_ID='id',
            HTTP_PAYPAL_TRANSMISSION_SIG='sig',
            HTTP_PAYPAL_TRANSMISSION_TIME='time'
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(UserPurchase.objects.filter(user=user, product=self.product).exists())

    @patch('paypal.views.verify_paypal_signature')
    def test_webhook_invalid_signature(self, mock_verify):
        mock_verify.return_value = False
        response = self.client.post(self.webhook_url, data='{}', content_type='application/json')
        self.assertEqual(response.status_code, 403)
