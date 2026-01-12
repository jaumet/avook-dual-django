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
    ProductTranslation.objects.create(
        product=product_start, language_code='de', name='Dual Start', description='Stufen A0 & A1'
    )
    ProductTranslation.objects.create(
        product=product_start, language_code='es', name='Dual Start', description='Niveles A0 y A1'
    )
    ProductTranslation.objects.create(
        product=product_start, language_code='fr', name='Dual Start', description='Niveaux A0 & A1'
    )
    ProductTranslation.objects.create(
        product=product_start, language_code='it', name='Dual Start', description='Livelli A0 e A1'
    )
    ProductTranslation.objects.create(
        product=product_start, language_code='pt', name='Dual Start', description='Níveis A0 e A1'
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
    ProductTranslation.objects.create(
        product=product_progress, language_code='de', name='Dual Progress', description='Stufen A2 & B1'
    )
    ProductTranslation.objects.create(
        product=product_progress, language_code='es', name='Dual Progress', description='Niveles A2 y B1'
    )
    ProductTranslation.objects.create(
        product=product_progress, language_code='fr', name='Dual Progress', description='Niveaux A2 & B1'
    )
    ProductTranslation.objects.create(
        product=product_progress, language_code='it', name='Dual Progress', description='Livelli A2 e B1'
    )
    ProductTranslation.objects.create(
        product=product_progress, language_code='pt', name='Dual Progress', description='Níveis A2 e B1'
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
    ProductTranslation.objects.create(
        product=product_advanced, language_code='de', name='Dual Advanced', description='Stufen B2 & C1'
    )
    ProductTranslation.objects.create(
        product=product_advanced, language_code='es', name='Dual Advanced', description='Niveles B2 y C1'
    )
    ProductTranslation.objects.create(
        product=product_advanced, language_code='fr', name='Dual Advanced', description='Niveaux B2 & C1'
    )
    ProductTranslation.objects.create(
        product=product_advanced, language_code='it', name='Dual Advanced', description='Livelli B2 e C1'
    )
    ProductTranslation.objects.create(
        product=product_advanced, language_code='pt', name='Dual Advanced', description='Níveis B2 e C1'
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
    ProductTranslation.objects.create(
        product=product_full, language_code='de', name='Dual Full Access', description='Alle Stufen'
    )
    ProductTranslation.objects.create(
        product=product_full, language_code='es', name='Dual Full Access', description='Todos los niveles'
    )
    ProductTranslation.objects.create(
        product=product_full, language_code='fr', name='Dual Full Access', description='Tous les niveaux'
    )
    ProductTranslation.objects.create(
        product=product_full, language_code='it', name='Dual Full Access', description='Tutti i livelli'
    )
    ProductTranslation.objects.create(
        product=product_full, language_code='pt', name='Dual Full Access', description='Todos os níveis'
    )

    print("Database seeded successfully with new products and packages.")
