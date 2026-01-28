import json
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, Mock
from products.models import Product, UserPurchase, UserAccess
from paypal.models import PendingPayment
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class PayPalWebhookTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', pk=123)
        self.product = Product.objects.create(machine_name='test-product', price=10.00)
        self.webhook_url = reverse('paypal:webhook')
        self.pending = PendingPayment.objects.create(
            paypal_order_id='ORDER-123',
            user=self.user,
            product=self.product,
            status='pending'
        )

    @patch('paypal.views.verify_paypal_signature')
    @patch('paypal.views.send_purchase_confirmation_email')
    def test_webhook_payment_capture_completed(self, mock_send_email, mock_verify):
        mock_verify.return_value = True

        payload = {
            "event_type": "PAYMENT.CAPTURE.COMPLETED",
            "resource": {
                "id": "CAPTURE-123",
                "create_time": "2024-01-01T12:00:00Z",
                "custom_id": "123",
                "supplementary_data": {
                    "related_ids": {
                        "order_id": "ORDER-123"
                    }
                }
            }
        }

        response = self.client.post(
            self.webhook_url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        # Verify PendingPayment status
        self.pending.refresh_from_db()
        self.assertEqual(self.pending.status, 'paid')

        # Verify UserPurchase
        purchase = UserPurchase.objects.get(user=self.user, product=self.product)
        self.assertEqual(purchase.paypal_order_id, 'ORDER-123')
        self.assertEqual(purchase.paypal_capture_id, 'CAPTURE-123')
        self.assertEqual(purchase.status, 'completed')

        # Verify UserAccess
        access = UserAccess.objects.get(user=self.user, product=self.product)
        self.assertTrue(access.active)

        # Verify email was called
        mock_send_email.assert_called_once()

    @patch('paypal.views.verify_paypal_signature')
    def test_webhook_payment_capture_denied(self, mock_verify):
        mock_verify.return_value = True

        payload = {
            "event_type": "PAYMENT.CAPTURE.DENIED",
            "resource": {
                "id": "CAPTURE-123",
                "supplementary_data": {
                    "related_ids": {
                        "order_id": "ORDER-123"
                    }
                }
            }
        }

        response = self.client.post(
            self.webhook_url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        # Verify PendingPayment status
        self.pending.refresh_from_db()
        self.assertEqual(self.pending.status, 'failed')

        # Verify NO UserPurchase
        self.assertFalse(UserPurchase.objects.filter(user=self.user, product=self.product).exists())

    @patch('paypal.views.verify_paypal_signature')
    def test_webhook_payment_capture_refunded(self, mock_verify):
        mock_verify.return_value = True

        # Pre-create purchase and access
        UserPurchase.objects.create(
            user=self.user,
            product=self.product,
            paypal_order_id='ORDER-123',
            paypal_capture_id='CAPTURE-123',
            status='completed'
        )
        UserAccess.objects.create(user=self.user, product=self.product, active=True)

        payload = {
            "event_type": "PAYMENT.CAPTURE.REFUNDED",
            "resource": {
                "id": "CAPTURE-123",
                "supplementary_data": {
                    "related_ids": {
                        "order_id": "ORDER-123"
                    }
                }
            }
        }

        response = self.client.post(
            self.webhook_url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        # Verify UserPurchase status
        purchase = UserPurchase.objects.get(user=self.user, product=self.product)
        self.assertEqual(purchase.status, 'refunded')

        # Verify UserAccess deactivation
        access = UserAccess.objects.get(user=self.user, product=self.product)
        self.assertFalse(access.active)

    @patch('paypal.views.verify_paypal_signature')
    def test_webhook_invalid_signature(self, mock_verify):
        mock_verify.return_value = False
        response = self.client.post(self.webhook_url, data='{}', content_type='application/json')
        self.assertEqual(response.status_code, 400)

class PayPalServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser_service', email='testuser_service@example.com', pk=789)
        self.product = Product.objects.create(machine_name='service-product', price=20.00)

    @patch('requests.post')
    def test_create_payment_resource_success(self, mock_post):
        # Token response
        mock_token_response = Mock()
        mock_token_response.status_code = 200
        mock_token_response.json.return_value = {'access_token': 'fake_token'}

        # Order response
        mock_order_response = Mock()
        mock_order_response.status_code = 201
        mock_order_response.json.return_value = {
            'id': 'ORDER-XYZ',
            'links': [
                {'rel': 'approve', 'href': 'https://www.paypal.com/checkout/ORDER-XYZ'}
            ]
        }

        mock_post.side_effect = [mock_token_response, mock_order_response]

        from paypal.services import create_payment_resource
        link = create_payment_resource(
            product_name="Service Product",
            price=20.00,
            machine_name="service-product",
            user_id=789,
            product_id=self.product.id,
            return_url="http://localhost:8000/success"
        )

        self.assertEqual(link, 'https://www.paypal.com/checkout/ORDER-XYZ')

        # Verify PendingPayment created
        self.assertTrue(PendingPayment.objects.filter(paypal_order_id='ORDER-XYZ', user=self.user, product=self.product).exists())

class PayPalViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser_view', email='testuser_view@example.com', password='password', pk=101)
        self.product = Product.objects.create(machine_name='view-product', price=30.00)
        self.client.login(username='testuser_view', password='password')

    @patch('paypal.views.capture_paypal_order')
    def test_paypal_capture_view_success(self, mock_capture):
        mock_capture.return_value = {'status': 'COMPLETED'}

        url = reverse('products:success') + '?token=ORDER-123'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/success.html')
        mock_capture.assert_called_once_with('ORDER-123')

    @patch('paypal.views.create_payment_resource')
    def test_get_payment_link_view(self, mock_create):
        mock_create.return_value = 'https://paypal.com/link'

        url = reverse('paypal:create_payment_link', kwargs={'product_id': self.product.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['payment_link'], 'https://paypal.com/link')
        mock_create.assert_called_once()
        # Verify it passed product_id
        args, kwargs = mock_create.call_args
        self.assertEqual(kwargs['product_id'], self.product.id)
