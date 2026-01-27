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
