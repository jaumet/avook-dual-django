from django.db import models
from django.conf import settings

class PendingPayment(models.Model):
    paypal_order_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PendingPayment {self.paypal_order_id} - {self.status}"

    class Meta:
        verbose_name = "Pagament pendent"
        verbose_name_plural = "Pagaments pendents"
