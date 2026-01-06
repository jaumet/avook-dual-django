from products.models import Product, ProductTranslation, Package, Title

def run():
    # Clear existing products and packages to ensure a clean slate
    Product.objects.all().delete()
    Package.objects.all().delete()

    # Create Packages for each level and assign all titles of that level
    levels = ['A0', 'A1', 'A2', 'B1', 'B2', 'C1']
    packages = {}
    for level in levels:
        package, created = Package.objects.get_or_create(name=level, level=level)
        titles = Title.objects.filter(level=level)
        package.titles.set(titles)
        packages[level] = package

    # Product 1: Dual Start
    product_start = Product.objects.create(machine_name='dual-start', price=19, duration=3, category='start')
    product_start.packages.add(packages['A0'], packages['A1'])
    ProductTranslation.objects.create(
        product=product_start, language_code='ca', name='Dual Start', description='Nivells A0 i A1'
    )
    ProductTranslation.objects.create(
        product=product_start, language_code='en', name='Dual Start', description='Levels A0 & A1'
    )

    # Product 2: Dual Progress
    product_progress = Product.objects.create(machine_name='dual-progress', price=29, duration=3, category='progress')
    product_progress.packages.add(packages['A2'], packages['B1'])
    ProductTranslation.objects.create(
        product=product_progress, language_code='ca', name='Dual Progress', description='Nivells A2 i B1'
    )
    ProductTranslation.objects.create(
        product=product_progress, language_code='en', name='Dual Progress', description='Levels A2 & B1'
    )

    # Product 3: Dual Advanced
    product_advanced = Product.objects.create(machine_name='dual-advanced', price=36, duration=3, category='advanced')
    product_advanced.packages.add(packages['B2'], packages['C1'])
    ProductTranslation.objects.create(
        product=product_advanced, language_code='ca', name='Dual Advanced', description='Nivells B2 i C1'
    )
    ProductTranslation.objects.create(
        product=product_advanced, language_code='en', name='Dual Advanced', description='Levels B2 & C1'
    )

    # Product 4: Dual Full Access
    product_full = Product.objects.create(machine_name='dual-full-access', price=49, duration=6, category='full_access')
    product_full.packages.set(packages.values())
    ProductTranslation.objects.create(
        product=product_full, language_code='ca', name='Dual Full Access', description='Tots els nivells'
    )
    ProductTranslation.objects.create(
        product=product_full, language_code='en', name='Dual Full Access', description='All levels'
    )

    print("Database seeded successfully with new products and packages.")
