
import os
import django

def seed():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avook_site.settings')
    django.setup()

    from products.models import Product, Package

    # Clean up existing products to start fresh
    Product.objects.all().delete()
    print("Old products deleted.")

    # --- Dual Start ---
    dual_start_package = Package.objects.filter(name__icontains="dual start").first()
    if dual_start_package:
        Product.objects.create(
            name="Dual Start",
            price="25.00",
            description="Access to the Dual Start package for 3 months.",
            category='dual_start',
            duration=3,
        ).packages.add(dual_start_package)
        print("Dual Start product created.")

    # --- Dual Progress ---
    levels = ["A2", "B1", "B2", "C1"]
    for level in levels:
        package = Package.objects.filter(name__icontains=f"dual progress {level}").first()
        if package:
            # Standard Dual Progress
            Product.objects.create(
                name=f"Dual Progress {level}",
                price="40.00",
                description=f"Access to the Dual Progress {level} package for 3 months.",
                category='dual_progress',
                duration=3,
            ).packages.add(package)
            print(f"Dual Progress {level} product created.")

            # Dual Progress + Extra Language
            Product.objects.create(
                name=f"Dual Progress {level} + Extra Language",
                price="48.00",
                description=f"Access to the Dual Progress {level} package with an extra language for 3 months.",
                category='dual_progress',
                duration=3,
            ).packages.add(package)
            print(f"Dual Progress {level} + Extra Language product created.")

    # --- Dual Full Access ---
    full_access_package = Package.objects.filter(name__icontains="dual full access").first()
    if full_access_package:
        # 3 Months
        Product.objects.create(
            name="Dual Full Access (3 Months)",
            price="100.00",
            description="Full access to all titles for 3 months.",
            category='dual_full_access',
            duration=3,
        ).packages.add(full_access_package)
        print("Dual Full Access (3 Months) product created.")

        # 6 Months
        Product.objects.create(
            name="Dual Full Access (6 Months)",
            price="180.00",
            description="Full access to all titles for 6 months.",
            category='dual_full_access',
            duration=6,
        ).packages.add(full_access_package)
        print("Dual Full Access (6 Months) product created.")

if __name__ == "__main__":
    seed()
