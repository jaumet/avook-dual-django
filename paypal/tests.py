import json
import unittest
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, Mock
from products.models import Product, UserPurchase
from django.contrib.auth import get_user_model

User = get_user_model()

class PayPalWebhookTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', pk=123)
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
        user = User.objects.create_user(username='testuser2', email='testuser2@example.com', pk=456)

        payload = {
            "event_type": "PAYMENT.CAPTURE.COMPLETED",
            "resource": {
                "purchase_units": [
                    {
                        "items": [
                            {
                                "sku": "test-product__456"
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

class PayPalServiceTest(TestCase):
    def setUp(self):
        if not User.objects.filter(pk=789).exists():
            self.user = User.objects.create_user(username='testuser_service', email='testuser_service@example.com', pk=789)
        else:
            self.user = User.objects.get(pk=789)
        self.product = Product.objects.create(machine_name='service-product', price=20.00)

    @patch('paypal.services.get_paypal_access_token')
    @patch('requests.post')
    def test_create_payment_resource_success(self, mock_post, mock_get_token):
        mock_get_token.return_value = 'fake_token'

        # Token response
        mock_token_response = Mock()
        mock_token_response.status_code = 200
        mock_token_response.json.return_value = {'access_token': 'fake_token'}

        # Order response
        mock_order_response = Mock()
        mock_order_response.status_code = 201
        mock_order_response.json.return_value = {
            'links': [
                {'rel': 'approve', 'href': 'https://www.paypal.com/ncp/payment/PLB-XYZ'}
            ]
        }

        mock_post.side_effect = [mock_token_response, mock_order_response]

        from paypal.services import create_payment_resource
        link = create_payment_resource(
            product_name="Service Product",
            price=20.00,
            machine_name="service-product",
            user_id=789,
            return_url="http://localhost:8000/success"
        )

        self.assertEqual(link, 'https://www.paypal.com/ncp/payment/PLB-XYZ')

        # Verify payload
        args, kwargs = mock_post.call_args
        payload = kwargs['json']
        self.assertEqual(payload['intent'], 'CAPTURE')
        self.assertEqual(payload['purchase_units'][0]['custom_id'], '789')

class PayPalViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        if not User.objects.filter(username='testuser_view').exists():
            self.user = User.objects.create_user(username='testuser_view', email='testuser_view@example.com', password='password', pk=101)
        else:
            self.user = User.objects.get(username='testuser_view')
        self.product = Product.objects.create(machine_name='view-product', price=30.00)
        self.client.login(username='testuser_view', password='password')

    @patch('paypal.views.create_payment_resource')
    def test_get_payment_link_view(self, mock_create):
        mock_create.return_value = 'https://paypal.com/link'

        url = reverse('paypal:create_payment_link', kwargs={'product_id': self.product.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['payment_link'], 'https://paypal.com/link')
