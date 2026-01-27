from django.db import migrations

def update_site_name(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    # Update the default site (usually ID=1)
    Site.objects.update_or_create(
        id=1,
        defaults={
            'domain': 'dual.cat',
            'name': 'Dual'
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_customuser_options'),
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_site_name),
    ]
