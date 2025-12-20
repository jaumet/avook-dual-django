import datetime
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from products.models import Product, Title, Package, UserPurchase

class ProductAccessTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='password')

        self.level_a2_package = Package.objects.create(name='A2 Package', level_range='A2')
        self.title_a2 = Title.objects.create(machine_name='a2-title', human_name='A2 Title', levels='A2')
        self.level_a2_package.titles.add(self.title_a2)

        self.product_a2 = Product.objects.create(
            name='Dual Progress A2',
            price=39.99,
            duration=3,
            category='progress'
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
