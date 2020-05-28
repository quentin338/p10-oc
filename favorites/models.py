from django.db import models
from django.conf import settings

from .manager import FavoriteManager


class Favorite(models.Model):
    class Meta:
        unique_together = (('user', 'new_product', 'ancient_product'),)

    objects = FavoriteManager()

    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    new_product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name="new_product")
    ancient_product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name="ancient_product")
