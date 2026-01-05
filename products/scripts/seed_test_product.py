from products.models import Title, Package, Product, ProductTranslation

def run():
    title, _ = Title.objects.get_or_create(machine_name='Test-1', level='A1')
    package, _ = Package.objects.get_or_create(name='Test Package', level='A1')
    package.titles.add(title)
    product, _ = Product.objects.get_or_create(machine_name='test-product', price=10.00, currency='euro', category='start', duration=1)
    product.packages.add(package)
    ProductTranslation.objects.get_or_create(product=product, language_code='en', name='Test Product', description='This is a test product.')
    ProductTranslation.objects.get_or_create(product=product, language_code='ca', name='Producte de Prova', description='Això és un producte de prova.')
