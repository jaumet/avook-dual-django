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
