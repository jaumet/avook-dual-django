import os
import django

def seed():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avook_site.settings')
    django.setup()
    from products.models import Product, Package, Title, UserPurchase

    # Clean existing data
    Product.objects.all().delete()
    Package.objects.all().delete()
    UserPurchase.objects.all().delete()
    print("Cleared existing products, packages, and user purchases.")

    # Create packages for each level
    levels = ['A2', 'B1', 'B2', 'C1']
    level_packages = {}
    for level in levels:
        package, created = Package.objects.get_or_create(
            name=f'Dual {level}',
            level_range=level,
            defaults={'description': f'Contingut del nivell {level}'}
        )
        titles = Title.objects.filter(levels=level)
        package.titles.set(titles)
        level_packages[level] = package
        print(f"Created package for level {level} with {titles.count()} titles.")

    # Package for extra language
    extra_lang_package, created = Package.objects.get_or_create(
        name='Paquet de llengua extra',
        defaults={'description': 'Paquet amb títols amb moltes llengües'}
    )
    extra_lang_title = Title.objects.filter(machine_name='Trobada-a-l-exposicio').first()
    if extra_lang_title:
        extra_lang_package.titles.add(extra_lang_title)
        print("Created extra language package.")

    # Package for full access
    full_access_package, created = Package.objects.get_or_create(
        name='Accés complet',
        defaults={'description': 'Accés a tots els continguts'}
    )
    full_access_package.titles.set(Title.objects.all())
    print("Created full access package.")

    # Create products
    # 1. Dual Start
    product_start = Product.objects.create(
        name='Dual Start',
        price=29.99,
        description='Accés durant 3 mesos al nivell A2',
        duration=3,
        category='start'
    )
    product_start.packages.add(level_packages['A2'])
    print("Created product: Dual Start")

    # 2. Dual Progress
    for level, package in level_packages.items():
        # Product without extra language
        product_progress = Product.objects.create(
            name=f'Dual Progress {level}',
            price=39.99,
            description=f'Accés durant 3 mesos al nivell {level}',
            duration=3,
            category='progress'
        )
        product_progress.packages.add(package)
        print(f"Created product: Dual Progress {level}")

        # Product with extra language
        if extra_lang_package:
            product_progress_extra = Product.objects.create(
                name=f'Dual Progress {level} + Llengua Extra',
                price=47.99,
                description=f'Accés durant 3 mesos al nivell {level} amb una llengua extra',
                duration=3,
                category='progress'
            )
            product_progress_extra.packages.add(package, extra_lang_package)
            print(f"Created product: Dual Progress {level} + Llengua Extra")

    # 3. Dual Full Access
    product_full_3m = Product.objects.create(
        name='Dual Full Access 3 Mesos',
        price=59.99,
        description='Accés complet a tots els continguts durant 3 mesos',
        duration=3,
        category='full_access'
    )
    product_full_3m.packages.add(full_access_package)
    print("Created product: Dual Full Access 3 Mesos")

    product_full_6m = Product.objects.create(
        name='Dual Full Access 6 Mesos',
        price=99.99,
        description='Accés complet a tots els continguts durant 6 mesos',
        duration=6,
        category='full_access'
    )
    product_full_6m.packages.add(full_access_package)
    print("Created product: Dual Full Access 6 Mesos")

if __name__ == "__main__":
    seed()
