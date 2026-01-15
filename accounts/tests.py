from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
from .forms import SignUpForm
from post_office.models import EmailTemplate, EmailTemplateTranslation

User = get_user_model()

class SignUpFormTest(TestCase):
    def test_new_user_is_inactive_and_has_token(self):
        """
        Verify that a newly created user is inactive and has a confirmation token.
        """
        form_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        form = SignUpForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors.as_json())
        user = form.save()
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIsNotNone(user.confirmation_token)

class AccountsURLTest(TestCase):
    def test_all_account_urls_resolve(self):
        """
        Verify that all URLs in the 'accounts' namespace resolve correctly.
        """
        User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

        # Test URLs that don't require arguments
        simple_urls = [
            'signup', 'login', 'logout', 'password_reset',
            'password_reset_done', 'password_reset_complete', 'profile',
            'purchase_history', 'activity', 'activity_pdf'
        ]
        for url_name in simple_urls:
            url = reverse(f'accounts:{url_name}')
            response = self.client.get(url)
            self.assertNotEqual(response.status_code, 404)


class SignUpEmailTest(TestCase):
    @patch('post_office.utils.send_email')
    def test_signup_sends_activation_email(self, mock_send_email):
        """
        Verify that signing up a new user sends an activation email.
        """
        form_data = {
            'username': 'emailtestuser',
            'first_name': 'Email',
            'last_name': 'Test',
            'email': 'emailtest@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        response = self.client.post(reverse('accounts:signup'), form_data)
        self.assertEqual(response.status_code, 302) # Should redirect on success

        mock_send_email.assert_called_once()
        _, kwargs = mock_send_email.call_args
        self.assertEqual(kwargs['to'], ['emailtest@example.com'])
