import uuid
import re
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.adapter import CustomAccountAdapter

User = get_user_model()

class CustomAccountAdapterTest(TestCase):
    def test_generate_unique_username_min_length(self):
        adapter = CustomAccountAdapter()
        # Even with short input, should be at least 5 chars
        username = adapter.generate_unique_username(['abc'])
        self.assertGreaterEqual(len(username), 5)
        self.assertTrue(re.match(r'^[a-zA-Z0-9]+$', username))

    def test_generate_unique_username_alphanumeric(self):
        adapter = CustomAccountAdapter()
        # Should remove dots and special chars
        username = adapter.generate_unique_username(['test.user@example.com'])
        self.assertTrue(re.match(r'^[a-zA-Z0-9]+$', username))
        self.assertNotIn('.', username)

class AuthFlowTest(TestCase):
    def test_login_url_redirects_to_request_code(self):
        url = reverse('account_login')
        response = self.client.get(url)
        # We set it to redirect to account_request_login_code
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('account_request_login_code'), response.url)

    def test_request_login_code_view(self):
        url = reverse('account_request_login_code')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/request_login_code.html')

    def test_confirm_login_code_view_redirects_if_no_session(self):
        url = reverse('account_confirm_login_code')
        response = self.client.get(url)
        # Should redirect back to request code if no login stage in session
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('account_request_login_code'), response.url)

from accounts.forms import ProfileUpdateForm

class ProfileUpdateFormTest(TestCase):
    def test_first_name_and_last_name_required(self):
        form = ProfileUpdateForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)
        self.assertIn('last_name', form.errors)

    def test_first_name_must_contain_letter(self):
        form = ProfileUpdateForm(data={'first_name': '123', 'last_name': 'Test', 'email': 'test@example.com'})
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    def test_last_name_must_contain_letter(self):
        form = ProfileUpdateForm(data={'first_name': 'Test', 'last_name': '123', 'email': 'test@example.com'})
        self.assertFalse(form.is_valid())
        self.assertIn('last_name', form.errors)

class RedirectOnFirstLoginTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        self.adapter = CustomAccountAdapter()

    def test_redirect_on_first_login(self):
        self.assertTrue(self.user.is_first_login)
        # Mock request with user
        class MockRequest:
            def __init__(self, user):
                self.user = user

        request = MockRequest(self.user)
        redirect_url = self.adapter.get_login_redirect_url(request)

        self.assertIn(reverse('accounts:profile'), redirect_url)
        self.assertIn('edit=1', redirect_url)

        # Reload user from DB to check if is_first_login was updated
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_first_login)

class ActivateAccountTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='activeuser',
            email='active@example.com',
            password='password123',
            is_active=False
        )
        self.user.confirmation_token = uuid.uuid4()
        self.user.save()

    def test_activate_account_logs_in_and_redirects(self):
        url = reverse('accounts:activate', kwargs={'token': str(self.user.confirmation_token)})
        response = self.client.get(url)

        # Reload user
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertTrue(self.user.email_confirmed)

        # Check login
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

        # Check redirect (first login)
        self.assertRedirects(response, reverse('accounts:profile') + "?edit=1")
        self.assertFalse(self.user.is_first_login)

class AllauthTemplateTest(TestCase):
    def test_verification_sent_template_extends_base(self):
        url = reverse('account_email_verification_sent')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/verification_sent.html')
        self.assertContains(response, '<header class="main-header">')
