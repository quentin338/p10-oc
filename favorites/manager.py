from django.db import models
from django.db.utils import IntegrityError


class FavoriteManager(models.Manager):
    def is_favorite(self, user, ancient_product, new_product):
        return bool(self.filter(user=user, ancient_product=ancient_product,
                                new_product=new_product))
