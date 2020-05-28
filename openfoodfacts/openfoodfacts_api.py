import json
import re
import html

import requests


class OpenFoodFactsException(Exception):
    pass


class OpenFoodFactsAPI:
    _OFF_URL = "https://fr.openfoodfacts.org/"
    _PRODUCTS_BY_PAGE = 250
    _PRODUCTS_URL = "https://fr.openfoodfacts.org/cgi/search.pl"

    def __init__(self, number_categories, number_products_by_category, categories=None):
        self._number_categories = number_categories
        self._number_products_by_category = number_products_by_category
        self.categories = categories or self._get_categories()

    def _get_categories(self) -> list:
        """
        Get self.number_categories categories from OFF

        :return: list of categories names

        """
        params = {
            "json": "true"
        }

        response = requests.get(self._OFF_URL + "categories", params=params)

        if not response.content or response.status_code != 200:
            raise OpenFoodFactsException(f"Error when retrieving categories : Status code - {response.status_code}, "
                                         f"response.content - {response.content}")

        try:
            response_json = json.loads(response.content)
            categories = response_json['tags'][:self._number_categories]
        except (TypeError, KeyError):
            raise OpenFoodFactsException(f"Error when retrieving categories : response.content = {response.content}")

        list_categories = []
        for category in categories:
            list_categories.append(category['name'])

        return list_categories

    def get_products(self) -> dict:
        """
        Get generator of products dictionary with name/category/image_url/nutriscore/ingredients_image_url/code

        :return: product dict

        """
        unique_products = set()

        for category in self.categories:
            products_added = 0
            page_number = 1

            while products_added < self._number_products_by_category:
                # Filtering products
                params = {
                    'action': 'process',
                    'tagtype_0': 'countries',
                    'tag_contains_0': 'contains',
                    'tag_0': 'fr',
                    'tagtype_1': 'languages',
                    'tag_contains_1': 'contains',
                    'tag_1': 'fr',
                    'tagtype_2': 'categories',
                    'tag_contains_2': 'contains',
                    'tag_2': category,
                    'sort_by': 'unique_scans_n',
                    'page_size': str(self._PRODUCTS_BY_PAGE),
                    'page': str(page_number),
                    'json': 'true',
                    'fields': 'code,product_name_fr,image_url,'
                              'nutriscore_score,nutriscore_grade,selected_images,'
                              'countries_lc,categories_lc,labels_lc'
                }

                response = requests.get(self._PRODUCTS_URL, params=params)

                if not response.content or response.status_code != 200:
                    raise OpenFoodFactsException(f"Error when retrieving products from category : {category}, "
                                                 f"status_code - {response.status_code}")

                try:
                    response_json = json.loads(response.content)
                    products = response_json['products']
                except (TypeError, KeyError):
                    raise OpenFoodFactsException(f"Error when retrieving products from category : {category}, "
                                                 f"response.content - {response.content}")

                for product in products:
                    if not self._check_product_is_fr(product):
                        continue

                    try:
                        product_dict = {
                            'code': product['code'],
                            'name': html.unescape(product['product_name_fr']),
                            'image_url': product['image_url'],
                            'nutriscore': product['nutriscore_score'],
                            'nutriscore_grade': product['nutriscore_grade'],
                            'ingredients_image': product['selected_images']['ingredients']['display']['fr'],
                            'category': category
                        }
                    except KeyError:
                        continue

                    # One value is missing or the grade is not valid
                    # or product name is breaking 150 chars long constraint
                    product_values = set(product_dict.values())
                    if "" in product_values or not re.fullmatch("[a-eA-E]", product_dict['nutriscore_grade'])\
                            or len(product_dict['name']) > 150:
                        continue

                    # Checking that the product is unique based on his name
                    # To avoid breaking unicity constraint SQL side
                    product_name = product_dict['name']
                    if product_name in unique_products:
                        continue
                    else:
                        unique_products.add(product_name)

                    yield product_dict

                    # To stop if we reach the number of products required
                    products_added += 1
                    if products_added == self._number_products_by_category:
                        break

                # We don't reach the target number of products so we go to the next page
                page_number += 1

    @staticmethod
    def _check_product_is_fr(product: dict) -> bool:
        """
        Return True if product is French. Some products can fake their way through even with this check

        :param product: dict of the product
        :return: bool - is French
        """
        keys_to_check = ['countries_lc', 'categories_lc', 'labels_lc']

        for key in keys_to_check:
            if "fr" not in product.get(key, ""):
                return False

        return True


if __name__ == "__main__":
    import timeit
    api = OpenFoodFactsAPI(number_categories=10, number_products_by_category=100)

    print(timeit.timeit("for prod in api.get_products(): print(prod)", globals=globals(), number=1))
    # for prod in api.get_products():
    #     print(prod)

