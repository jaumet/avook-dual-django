from django.db import models
from django.urls import reverse


class Product(models.Model):
    title = models.CharField(max_length=200)
    language_pair = models.CharField(
        max_length=100, help_text='Exemple: Català - Anglès'
    )
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    audio_file = models.FileField(
        upload_to='audios/', blank=True, null=True, help_text='Arxiu d\'àudio opcional'
    )
    cover_image = models.CharField(
        max_length=255,
        blank=True,
        help_text='Ruta de la imatge a /static/imgs o /media',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('products:detail', args=[self.pk])
