
import os
import django

def seed():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avook_site.settings')
    django.setup()

    from products.models import Package, Title

    # Clean up existing packages to start fresh
    Package.objects.all().delete()
    print("Old packages deleted.")

    # --- Create Packages ---
    packages_to_create = {
        "Dual Start": ["A0", "A1"],
        "Dual Progress A2": ["A2"],
        "Dual Progress B1": ["B1"],
        "Dual Progress B2": ["B2"],
        "Dual Progress C1": ["C1"],
        "Dual Full Access": ["A0", "A1", "A2", "B1", "B2", "C1", "C2"],
    }

    for name, levels in packages_to_create.items():
        package = Package.objects.create(name=name)
        titles = Title.objects.filter(levels__in=levels)
        package.titles.add(*titles)
        print(f"Created package '{name}' with {titles.count()} titles.")

if __name__ == "__main__":
    seed()
