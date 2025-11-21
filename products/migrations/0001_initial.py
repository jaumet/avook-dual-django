from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('language_pair', models.CharField(help_text='Exemple: Català - Anglès', max_length=100)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                (
                    'audio_file',
                    models.FileField(
                        blank=True,
                        help_text="Arxiu d'àudio opcional",
                        null=True,
                        upload_to='audios/',
                    ),
                ),
                (
                    'cover_image',
                    models.CharField(
                        blank=True,
                        help_text='Ruta de la imatge a /static/imgs o /media',
                        max_length=255,
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['title']},
        ),
    ]
