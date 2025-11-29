from django.test import TestCase
from django.contrib.auth import get_user_model
from .forms import SignUpForm

class SignUpFormTest(TestCase):
    def test_new_user_has_no_permissions(self):
        """
        Verify that a newly created user does not have staff or superuser permissions.
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
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors.as_json()}")

        user = form.save()
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
