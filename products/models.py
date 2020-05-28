from django.db import models

from products.manager import ProductManager


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    code = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=150, unique=True)
    image_url = models.CharField(max_length=200)
    nutriscore = models.SmallIntegerField()
    nutriscore_grade = models.CharField(max_length=1)
    ingredients_image = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')

    objects = ProductManager()

    def __str__(self):
        return self.name

    @property
    def nutriscore_img(self):
        """
        Get the name of the nutriscore png relative to the nutriscore grade of the product
        :return: the name (str) of the file

        """
        if len(self.nutriscore_grade) != 1:
            self.nutriscore_grade = "d"

        nutriscore_img = f"nutriscore_{self.nutriscore_grade}.png"
        return nutriscore_img

    @property
    def nutriscore_full_img(self):
        """
        Get the name of the full nutriscore png relative to the nutriscore grade of the product
        :return: the name (str) of the file

        """
        if len(self.nutriscore_grade) != 1:
            self.nutriscore_grade = "d"

        nutriscore_full_img = f"nutriscore_full_{self.nutriscore_grade}.svg"
        return nutriscore_full_img

    @property
    def url(self):
        openff_url = "https://fr.openfoodfacts.org/produit/"
        product_url = openff_url + str(self.code)
        return product_url


