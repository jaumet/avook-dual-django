from django.test import TestCase
from django.contrib.auth import get_user_model
from .forms import SignUpForm
from django.urls import reverse
from django.utils import translation

User = get_user_model()

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
            'password2': 'testpassword',
            'password': 'testpassword',
        }
        form = SignUpForm(data=form_data)

        # Manually set password1 and password2 as they are not part of the form's Meta.fields
        form.data['password1'] = 'testpassword'
        form.data['password2'] = 'testpassword'

        if form.is_valid():
            user = form.save()
            self.assertFalse(user.is_staff)
            self.assertFalse(user.is_superuser)
        else:
            self.fail(f"Form errors: {form.errors.as_json()}")

from django.core.management import call_command
import json
from .models import TranslatableContent

class HomeViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_home_page_renders_for_authenticated_user(self):
        """
        Verify that the home page renders successfully for an authenticated user.
        """
        self.client.login(username='testuser', password='testpassword')
        with translation.override('ca'):
            response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

class ContentManagementTest(TestCase):
    def test_admin_edits_are_not_overwritten(self):
        """
        Verify that changes made in the admin are not overwritten by the populate_content command.
        """
        # 1. Initially populate the content
        call_command('populate_content')

        # 2. Simulate an admin edit
        home_content = TranslatableContent.objects.get(key='home_content')
        edited_json = json.loads(home_content.content_ca)
        edited_json['cta_title'] = "Aquest és un títol editat"
        home_content.content_ca = json.dumps(edited_json)
        home_content.save()

        # 3. Re-run the populate_content command
        call_command('populate_content')

        # 4. Verify that the changes persist
        home_content.refresh_from_db()
        final_json = json.loads(home_content.content_ca)
        self.assertEqual(final_json['cta_title'], "Aquest és un títol editat")

    def test_home_page_renders_for_anonymous_user(self):
        """
        Verify that the home page renders successfully for an anonymous user.
        """
        with translation.override('ca'):
            response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
