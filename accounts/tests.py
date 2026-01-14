from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .forms import SignUpForm

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
