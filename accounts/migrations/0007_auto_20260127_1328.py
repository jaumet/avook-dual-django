from django.db import migrations

def delete_non_admin_users(apps, schema_editor):
    User = apps.get_model('accounts', 'CustomUser')
    # Delete users who are NOT superusers AND NOT staff
    # This matches the user's request: "Excepte l'usuari administrador, pot eliminar els altres usuaris"
    User.objects.filter(is_superuser=False, is_staff=False).delete()

def ensure_site_config(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    Site.objects.update_or_create(
        id=1,
        defaults={
            'domain': 'dual.cat',
            'name': 'Dual'
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20260127_1323'),
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(delete_non_admin_users),
        migrations.RunPython(ensure_site_config),
    ]
