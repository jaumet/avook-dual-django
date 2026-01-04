from django.db import migrations

def migrate_product_data(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    ProductTranslation = apps.get_model('products', 'ProductTranslation')

    for product in Product.objects.all():
        ProductTranslation.objects.create(
            product=product,
            language_code='ca',
            name=product.name,
            description=product.description
        )

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0014_remove_product_description_remove_product_name_and_more'),
    ]

    operations = [
        migrations.RunPython(migrate_product_data),
    ]
