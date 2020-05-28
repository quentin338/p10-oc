from django.db import models


class ProductManager(models.Manager):
    def search_autocomplete(self, user_search):
        results = super().get_queryset().filter(name__icontains=user_search) \
                      .order_by('-nutriscore')[:10]

        results = [product.name for product in results]

        return results

    def get_old_product(self, user_search):
        old_product = super().get_queryset().filter(models.Q(name=user_search) |
                                                    models.Q(name__icontains=user_search) |
                                                    models.Q(name__icontains=user_search.capitalize()))\
                                            .first()

        return old_product

    def get_better_products(self, old_product):
        # product_category = Product.objects.filter(name=user_search).first().category
        product_category = old_product.category
        better_products = product_category.products.order_by('nutriscore')[:6]

        return better_products
