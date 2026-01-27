from django.db import migrations

def set_site_domain(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    Site.objects.filter(id=1).update(domain='dual.cat', name='Dual')

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_customuser_options'),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(set_site_domain),
    ]
