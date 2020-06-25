import datetime as dt

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from products.models import Category, Product
from openfoodfacts.openfoodfacts_api import OpenFoodFactsAPI


class Command(BaseCommand):
    help = "Update the products that are present in the DB. None will be added."

    def handle(self, *args, **options):
        number_updated = 0

        categories = Category.objects.all()
        products = Product.objects.all()

        if not products or not categories:
            print("There is no product in the database. Please "
                  "do a 'python manage.py db_init -c X -p Y' first.")

        api = OpenFoodFactsAPI(len(categories), len(products))

        date_begin = dt.datetime.now()
        date_fmt = date_begin.strftime("%A %d %B %Y at %H:%M:%S")

        print(f"Beginning : {date_fmt}")
        print("Updating products...")

        for api_product in api.get_products():
            # Looking if the product is already in the db
            try:
                db_product = products.get(pk=api_product['code'])
            except Product.DoesNotExist:
                # print(f"Product not found in the db. {api_product}")
                # No corresponding product found. As we only update but not add, we pass
                continue

            # Updating the product
            db_product_updated = False
            for api_prod_attr in api_product.keys():
                if api_prod_attr in {"code", "category"}:
                    continue

                if hasattr(db_product, api_prod_attr):
                    setattr(db_product, api_prod_attr, api_product[api_prod_attr])
                    db_product_updated = True

            if db_product_updated:
                try:
                    db_product.save()
                # One product has changed it's name to one already existing in the db
                # with a different code...
                except IntegrityError:
                    continue

                number_updated += 1

        time_end = dt.datetime.now()
        time_end = time_end - date_begin

        print(f"Successfully updated {number_updated} products of the {len(products)} present "
              f"in the database. Took {time_end.seconds} seconds.")



