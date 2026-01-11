from django.test import TestCase
from django.contrib.auth import get_user_model
from .forms import SignUpForm
from django.urls import reverse
from django.utils import translation
import datetime
from django.utils import timezone
from products.models import Product, Title, Package, UserPurchase, ProductTranslation


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

class ProductAccessTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='password')

        self.level_a2_package = Package.objects.create(name='A2 Package', level='A2')
        self.title_a2 = Title.objects.create(machine_name='a2-title', level='A2')
        self.level_a2_package.titles.add(self.title_a2)

        self.product_a2 = Product.objects.create(
            price=39.99,
            duration=3,
            category='progress'
        )
        ProductTranslation.objects.create(
            product=self.product_a2,
            language_code='en',
            name='Dual Progress A2',
            description='Test Description'
        )
        self.product_a2.packages.add(self.level_a2_package)

    def test_access_without_purchase(self):
        status = self.title_a2.get_user_status(self.user)
        self.assertEqual(status, 'PREMIUM_NOT_OWNED')

    def test_access_with_active_purchase(self):
        UserPurchase.objects.create(user=self.user, product=self.product_a2)
        status = self.title_a2.get_user_status(self.user)
        self.assertEqual(status, 'PREMIUM_OWNED')

    def test_access_with_expired_purchase(self):
        purchase = UserPurchase.objects.create(user=self.user, product=self.product_a2)
        purchase.expiry_date = timezone.now() - datetime.timedelta(days=1)
        purchase.save()
        status = self.title_a2.get_user_status(self.user)
        self.assertEqual(status, 'PREMIUM_NOT_OWNED')

    def test_access_with_null_expiry(self):
        # Simulate a purchase made before the expiry_date feature was added
        purchase = UserPurchase.objects.create(user=self.user, product=self.product_a2)
        purchase.expiry_date = None
        purchase.save()
        status = self.title_a2.get_user_status(self.user)
        self.assertEqual(status, 'PREMIUM_OWNED')


import os
import json
import shutil
import tempfile
from django.conf import settings
from django.test import override_settings

@override_settings(STATICFILES_DIRS=[tempfile.gettempdir()])
class PlayerViewTest(TestCase):
    def setUp(self):
        self.test_title_machine_name = 'Test-1'
        self.non_existent_title = 'non-existent-title'
        Title.objects.create(machine_name=self.test_title_machine_name, level='A0')

        # Create a temporary directory for static files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        # Define paths for mock files and directories within the temporary directory
        self.audios_dir = os.path.join(self.temp_dir.name, 'static', 'AUDIOS')
        self.level_dir = os.path.join(self.audios_dir, 'A0')
        os.makedirs(self.level_dir, exist_ok=True)

        # Override the BASE_DIR setting to point to the temporary directory
        settings.BASE_DIR = self.temp_dir.name

        # Create a mock audios.json
        self.audios_json_path = os.path.join(self.audios_dir, 'audios.json')
        mock_audios_data = {
            "AUDIOS": [{
                "machine_name": "Test-1",
                "levels": "A0",
                "text_versions": [
                    {"lang": "CA", "human-title": "Test CAT", "description": "Descripció CAT", "json_file": "Test-1-CA.json"},
                    {"lang": "EN", "human-title": "Test ENG", "description": "Description ENG", "json_file": "Test-1-EN.json"},
                    {"lang": "ES", "human-title": "Test ESP", "description": "Description ESP", "json_file": "Test-1-ES.json"},
                    {"lang": "DE", "human-title": "Test DEU", "description": "Description DEU", "json_file": "Test-1-DE.json"}
                ]
            }]
        }
        with open(self.audios_json_path, 'w') as f:
            json.dump(mock_audios_data, f)

        # Create mock title-specific JSON files
        mock_transcript_data = [{"file": "0001.mp3", "text": "This is a test."}]
        self.transcript_path_en = os.path.join(self.level_dir, 'Test-1-EN.json')
        with open(self.transcript_path_en, 'w') as f:
            json.dump(mock_transcript_data, f)

        self.transcript_path_ca = os.path.join(self.level_dir, 'Test-1-CA.json')
        with open(self.transcript_path_ca, 'w') as f:
            json.dump(mock_transcript_data, f)

    def test_player_view_with_existing_title(self):
        """
        Verify that the player view correctly loads data from audios.json.
        """
        # Test with English language
        with translation.override('en'):
            response = self.client.get(reverse('products:player', kwargs={'machine_name': self.test_title_machine_name}))
            self.assertEqual(response.status_code, 200)
            self.assertIn('title', response.context)
            self.assertIn('transcript', response.context)
            self.assertIn('audio_path_prefix', response.context)

            title_context = response.context['title']
            self.assertEqual(title_context['machine_name'], 'Test-1')
            self.assertEqual(title_context['human_title'], 'Test ENG')
            self.assertEqual(title_context['description'], 'Description ENG')
            self.assertEqual(title_context['languages'], ['CA', 'EN', 'ES', 'DE'])

            self.assertContains(response, '<h2 id="relatTitle">Test ENG</h2>')
            self.assertContains(response, '<div id="relatDesc" style="margin:.1em 0 .3em 0;">Description ENG</div>')

        # Test with Catalan language to check translation
        with translation.override('ca'):
            response = self.client.get(reverse('products:player', kwargs={'machine_name': self.test_title_machine_name}))
            self.assertEqual(response.status_code, 200)
            title_context = response.context['title']
            self.assertEqual(title_context['human_title'], 'Test CAT')
            self.assertEqual(title_context['description'], 'Descripció CAT')
            self.assertContains(response, '<h2 id="relatTitle">Test CAT</h2>')

    def test_player_view_with_non_existent_title(self):
        """
        Verify that the player view returns a 404 for a non-existent title.
        """
        response = self.client.get(reverse('products:player', kwargs={'machine_name': self.non_existent_title}))
        self.assertEqual(response.status_code, 404)

    def test_player_view_audio_path_prefix(self):
        """
        Verify that the audio_path_prefix in the player view is correct and does not contain the language code.
        """
        with translation.override('en'):
            response = self.client.get(reverse('products:player', kwargs={'machine_name': self.test_title_machine_name}))
            self.assertEqual(response.status_code, 200)
            self.assertIn('audio_path_prefix', response.context)
            expected_prefix = f"/static/AUDIOS/A0/{self.test_title_machine_name}/"
            self.assertEqual(response.context['audio_path_prefix'], expected_prefix)
