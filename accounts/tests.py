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

    def test_valid_names(self):
        form = ProfileUpdateForm(data={'first_name': 'Joan', 'last_name': 'García', 'email': 'test@example.com'})
        # known_languages and learning_languages are handled by JS, default to [] if empty but form might need them as empty strings
        self.assertTrue(form.is_valid())

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

    def test_no_redirect_on_subsequent_login(self):
        self.user.is_first_login = False
        self.user.save()

        class MockRequest:
            def __init__(self, user):
                self.user = user

        request = MockRequest(self.user)
        redirect_url = self.adapter.get_login_redirect_url(request)

        self.assertNotIn('edit=1', redirect_url)
        self.assertEqual(redirect_url, reverse('home')) # Default redirect
