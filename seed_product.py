import os
import django

def seed():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avook_site.settings')
    django.setup()
    from products.models import Product
    if not Product.objects.filter(id=30001).exists():
        Product.objects.create(id=30001, name="Test Product", price="10.00", description="A test product.")
        print("Product seeded.")
    else:
        print("Product already exists.")

if __name__ == "__main__":
    seed()
