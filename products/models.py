from django.db import models
from django.urls import reverse


class Title(models.Model):
    slug = models.SlugField(unique=True, help_text="Identificador únic del títol")
    title_human = models.CharField(max_length=255, help_text="Títol llegible")
    description = models.TextField(blank=True)
    level = models.CharField(max_length=10, help_text="Nivell del títol (A0, A1, …)")
    languages = models.CharField(max_length=255, help_text="Idiomes separats per comes")
    ages = models.CharField(max_length=50, blank=True, help_text="Rang d'edat recomanat")
    collection = models.CharField(max_length=255, blank=True)
    duration = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['title_human']

    def __str__(self):
        return self.title_human

    @property
    def language_list(self):
        return [lang.strip() for lang in self.languages.split(',') if lang.strip()]


class Product(models.Model):
    title = models.CharField(max_length=200)
    level = models.CharField(
        max_length=10,
        blank=True,
        help_text='Nivell del paquet (per exemple A0, A1, A2, B1, B2, C1, C2)',
    )
    language_pair = models.CharField(
        max_length=100, help_text='Exemple: Català - Anglès'
    )
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    audio_file = models.FileField(
        upload_to='audios/', blank=True, null=True, help_text="Arxiu d'àudio opcional"
    )
    cover_image = models.CharField(
        max_length=255,
        blank=True,
        help_text='Ruta de la imatge a /static/imgs o /media',
    )
    titles = models.ManyToManyField(Title, related_name='products', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('products:detail', args=[self.pk])
