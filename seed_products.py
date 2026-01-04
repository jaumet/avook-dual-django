from products.models import Product, ProductTranslation, Package, Title

# Clear existing products and packages to ensure a clean slate
Product.objects.all().delete()
Package.objects.all().delete()

# Create Packages
package_a1 = Package.objects.create(name='A1', level_range='A1')
package_a2 = Package.objects.create(name='A2', level_range='A2')
package_b1 = Package.objects.create(name='B1', level_range='B1')

# Add titles to packages
package_a1.titles.add(Title.objects.get(machine_name='0-1-Salutacions-i-emocions'))
package_a2.titles.add(Title.objects.get(machine_name='0-2-D-on-ets'))
package_b1.titles.add(Title.objects.get(machine_name='0-3-Bon-dia-bona-nit'))

# Create Products and Translations
# Product 1: Dual Start
product_start = Product.objects.create(price=29.99, duration=3, category='start')
product_start.packages.add(package_a1)
ProductTranslation.objects.create(
    product=product_start,
    language_code='ca',
    name='Dual Start',
    description='Accés durant 3 mesos al nivell A1'
)
ProductTranslation.objects.create(
    product=product_start,
    language_code='en',
    name='Dual Start',
    description='3-month access to level A1'
)

# Product 2: Dual Progress
product_progress = Product.objects.create(price=39.99, duration=3, category='progress')
product_progress.packages.add(package_a2)
ProductTranslation.objects.create(
    product=product_progress,
    language_code='ca',
    name='Dual Progress',
    description='Accés durant 3 mesos al nivell A2'
)
ProductTranslation.objects.create(
    product=product_progress,
    language_code='en',
    name='Dual Progress',
    description='3-month access to level A2'
)

# Product 3: Dual Full Access
product_full = Product.objects.create(price=99.99, duration=12, category='full_access')
product_full.packages.add(package_a1, package_a2, package_b1)
ProductTranslation.objects.create(
    product=product_full,
    language_code='ca',
    name='Dual Full Access',
    description='Accés durant 12 mesos a tots els nivells'
)
ProductTranslation.objects.create(
    product=product_full,
    language_code='en',
    name='Dual Full Access',
    description='12-month access to all levels'
)

print("Database seeded successfully with products and packages.")
