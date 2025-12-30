from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, is_password_usable
from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase
from django.urls import reverse
from django.utils import translation
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()


class AccountsURLTest(TestCase):
    def test_logout_url_works_with_post(self):
        """
        Verify that the logout URL resolves and redirects as expected on POST.
        """
        with translation.override('ca'):
            logout_url = reverse('accounts:logout')
        response = self.client.post(logout_url)
        self.assertEqual(response.status_code, 302)


class PasswordResetHashingTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='old_password'
        )

    def test_password_is_hashed_after_reset(self):
        """
        Tests that the password is not saved in plain text after a reset.
        """
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        new_password = 'new_plain_password'

        with translation.override('ca'):
            confirm_url = reverse('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})

        response = self.client.get(confirm_url)
        set_password_url = response.url

        self.client.post(set_password_url, {
            'new_password1': new_password,
            'new_password2': new_password,
        })

        self.user.refresh_from_db()

        # 1. The password should not be the plain text string.
        self.assertNotEqual(self.user.password, new_password, "The password should be hashed, not stored in plain text.")

        # 2. Django's is_password_usable() should return True for a hashed password.
        self.assertTrue(is_password_usable(self.user.password), "The password hash should be in a usable format.")

        # 3. check_password should correctly validate the new password.
        self.assertTrue(check_password(new_password, self.user.password), "check_password should succeed with the new password.")
