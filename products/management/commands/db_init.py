from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from products.models import Category, Product
from openfoodfacts.openfoodfacts_api import OpenFoodFactsAPI


class Command(BaseCommand):
    help = "Populate DB with Openfoodfacts categories and products"

    def add_arguments(self, parser):
        parser.add_argument('-c', nargs='?', type=int, help="Number of categories to be added", required=True)
        parser.add_argument('-p', nargs="?", type=int, help="Number of products added in each categories", required=True)

    def handle(self, *args, **options):
        number_categories = options['c']
        number_products = options['p']

        api = OpenFoodFactsAPI(number_categories, number_products)

        # Adding categories
        print(f"Adding {number_categories} categories", end="")
        for api_category in api.categories:
            category = Category(name=api_category)
            category.save()
            print(".", end="")

        # Adding products
        print(f"\nAdding {number_categories * number_products} products, it can take a little while...")

        for api_product in api.get_products():
            api_product['category'] = Category.objects.get(name=api_product['category'])
            product = Product(**api_product)

            # Taking care of duplicates if any (sanity check even with a set() in api.get_products())
            try:
                product.save()
            except IntegrityError:  # Unicity constraint
                continue

        print(f"\nSuccessfully added {len(Product.objects.all())} products and "
              f"{len(Category.objects.all())} categories. Differences may be duplicates.")


