from unittest import mock
import json
import copy

from django.test import TestCase, tag

from openfoodfacts.openfoodfacts_api import OpenFoodFactsAPI, OpenFoodFactsException


class TestOpenFoodFactsAPI(TestCase):

    def setUp(self) -> None:
        self.response_content_cat = json.dumps({
            "tags": [
                {
                    "name": "Charcuterie"
                },
                {
                    "name": "Boissons"
                }

            ]
        })
        self.response_content_prod = json.dumps({
            "products": [
                {
                    "code": 12345,
                    "product_name_fr": "Saucisson sec",
                    "image_url": "http://www.saucissonsec.com",
                    "nutrition_score_debug": "FR at the end of the string -- fr 10",
                    "nutriscore_grade": "a",
                    "category": "Charcuterie",
                    "countries_lc": "fr",
                    "categories_lc": "fr",
                    "labels_lc": "fr",
                    "selected_images": {
                        "ingredients": {
                            "display": {
                                'fr': "http://www.image.com"
                            }
                        }
                    }
                },
                {
                    "code": 999,
                    "product_name_fr": "Saucisson sec",
                    "image_url": "http://www.saucissonsec.com",
                    "nutrition_score_debug": "FR at the end of the string -- fr 10",
                    "nutriscore_grade": "a",
                    "category": "Charcuterie",
                    "countries_lc": "fr",
                    "categories_lc": "fr",
                    "labels_lc": "fr",
                    "selected_images": {
                        "ingredients": {
                            "display": {
                                'fr': "http://www.image.com"
                            }
                        }
                    }
                }
            ]
        })
        patcher = mock.patch("openfoodfacts.openfoodfacts_api.requests.get")
        self.addCleanup(patcher.stop)
        self.mock_requests = patcher.start()
        self.mock_requests.return_value = self.mock_response = mock.Mock()

    # _get_categories()
    def test_get_categories_len(self):
        self.mock_response.status_code = 200
        self.mock_response.content = self.response_content_cat

        api = OpenFoodFactsAPI(2, 2)
        self.assertEqual(2, len(api.categories))
        self.assertIn("Boissons", api.categories)
        self.assertIn("Charcuterie", api.categories)

    def test_get_categories_no_content(self):
        self.mock_response.content = ""
        self.mock_response.status_code = 200

        with self.assertRaises(OpenFoodFactsException, msg="No content doesn't raises Exception"):
            OpenFoodFactsAPI(1, 1)

    def test_get_categories_status_code_not_200(self):
        self.mock_response.content = self.response_content_cat
        self.mock_response.status_code = 404

        with self.assertRaises(OpenFoodFactsException,
                               msg="Status code != 200 doesn't raises Exception"):
            OpenFoodFactsAPI(1, 1)

    def test_get_categories_bad_response_content_key_error(self):
        self.mock_response.content = json.dumps({"Key": "Value"})
        self.mock_response.status_code = 200

        with self.assertRaises(OpenFoodFactsException,
                               msg="Bad response.content doesn't raise Exception"):
            OpenFoodFactsAPI(1, 1)

    def test_get_categories_bad_response_content_type_error(self):
        self.mock_response.content = json.dumps({"tags": 1})
        self.mock_response.status_code = 200

        with self.assertRaises(OpenFoodFactsException,
                               msg="Bad response.content doesn't raise Exception"):
            OpenFoodFactsAPI(1, 1)

    # get_products()
    @mock.patch("openfoodfacts.openfoodfacts_api.OpenFoodFactsAPI._check_product_is_fr",
                return_value=True)
    def test_get_products_proper_yield(self, mock_is_fr):
        self.mock_response.content = self.response_content_prod
        self.mock_response.status_code = 200

        api = OpenFoodFactsAPI(1, 1, ['Boissons'])

        product = next(api.get_products())
        self.assertEqual(json.loads(self.response_content_prod)['products'][0]['code'],
                         product['code'])

    def test_get_products_status_code_not_200(self):
        self.mock_response.content = self.response_content_prod
        self.mock_response.status_code = 404

        api = OpenFoodFactsAPI(1, 1, ["Boissons"])

        with self.assertRaises(OpenFoodFactsException,
                               msg="Don't raise Exception when Status Code != 200"):
            next(api.get_products())

    def test_get_products_no_response_content(self):
        self.mock_response.content = ""
        self.mock_response.status_code = 200

        api = OpenFoodFactsAPI(1, 1, ["Boissons"])

        with self.assertRaises(OpenFoodFactsException,
                               msg="Don't raise Exception when Status Code != 200"):
            next(api.get_products())

    def test_get_products_bad_response_content_key_error(self):
        self.mock_response.content = json.dumps({"Key": "Value"})
        self.mock_response.status_code = 200

        api = OpenFoodFactsAPI(1, 1, ['Boissons'])

        with self.assertRaises(OpenFoodFactsException,
                               msg="Don't raise Exception when bad API response"):
            next(api.get_products())

    def test_get_products_bad_response_content_type_error(self):
        self.mock_response.content = json.dumps("")
        self.mock_response.status_code = 200

        api = OpenFoodFactsAPI(1, 1, ['Boissons'])

        with self.assertRaises(OpenFoodFactsException,
                               msg="Don't raise Exception when bad API response"):
            next(api.get_products())

    @mock.patch("openfoodfacts.openfoodfacts_api.OpenFoodFactsAPI._check_product_is_fr",
                side_effect=[False, True])
    def test_get_products_continue_if_prod_not_french_proper_yield(self, mock_is_fr):
        self.mock_response.content = self.response_content_prod
        self.mock_response.status_code = 200

        api = OpenFoodFactsAPI(1, 1, ['Boissons'])

        product = next(api.get_products())
        # It yields the SECOND product
        self.assertEqual(json.loads(self.response_content_prod)['products'][1]['code'],
                         product['code'])

    @mock.patch("openfoodfacts.openfoodfacts_api.OpenFoodFactsAPI._check_product_is_fr",
                side_effect=[True, True])
    def test_get_products_continue_if_product_key_error(self, mock_is_fr):
        self.mock_response.status_code = 200
        # Adding that 3rd product at index 0 to get the KeyError and to yield something
        products = json.loads(self.response_content_prod)
        products['products'].insert(0, {"Key": "Value"})
        self.mock_response.content = json.dumps(products)

        api = OpenFoodFactsAPI(1, 1, ['Boissons'])

        product = next(api.get_products())

        self.assertEqual(json.loads(self.response_content_prod)['products'][0]['code'],
                         product['code'])

    @mock.patch("openfoodfacts.openfoodfacts_api.OpenFoodFactsAPI._check_product_is_fr",
                return_value=True)
    def test_get_products_continue_if_product_name_too_long(self, mock_is_fr):
        self.mock_response.status_code = 200
        # Modifying first product to have a name > 150
        products = json.loads(self.response_content_prod)
        products['products'][0]['product_name_fr'] = "z" * 160
        self.mock_response.content = json.dumps(products)

        api = OpenFoodFactsAPI(1, 1, ['Boissons'])

        product = next(api.get_products())

        # It should yield the SECOND product
        self.assertEqual(json.loads(self.response_content_prod)['products'][1]['code'],
                         product['code'])

    @mock.patch("openfoodfacts.openfoodfacts_api.OpenFoodFactsAPI._check_product_is_fr",
                return_value=True)
    def test_get_products_continue_if_bad_nutriscore(self, mock_is_fr):
        self.mock_response.status_code = 200
        # Modifying first product to have a bad nutriscore
        products = json.loads(self.response_content_prod)
        products['products'][0]['nutrition_score_debug'] = "string and not int -- fr"
        self.mock_response.content = json.dumps(products)

        api = OpenFoodFactsAPI(1, 1, ['Boissons'])

        product = next(api.get_products())

        # It should yield the SECOND product
        self.assertEqual(json.loads(self.response_content_prod)['products'][1]['code'],
                         product['code'])

    @mock.patch("openfoodfacts.openfoodfacts_api.OpenFoodFactsAPI._check_product_is_fr",
                return_value=True)
    def test_get_products_continue_if_product_name_already_registered(self, mock_is_fr):
        self.mock_response.status_code = 200
        # Adding a third product so that theirs names are X = X != Y
        products = json.loads(self.response_content_prod)
        new_prod = copy.deepcopy(products['products'][1])
        new_prod['product_name_fr'] = "New name to get yielded"
        new_prod['code'] = 987654321
        products['products'].append(new_prod)
        self.mock_response.content = json.dumps(products)

        api = OpenFoodFactsAPI(1, 2, ['Boissons'])

        # It should yield the 1st AND 3rd product as the second as the same name as the first
        products = []
        for prod in api.get_products():
            products.append(prod)

        self.assertEqual(new_prod['code'], products[1]['code'])

    # _check_product_is_fr()
    def test_check_fr_is_true(self):
        prod = json.loads(self.response_content_prod)['products'][0]
        api = OpenFoodFactsAPI(1, 1, ["Boissons"])

        is_fr = api._check_product_is_fr(prod)

        self.assertTrue(is_fr, msg="A French product is considerer as non-French.")

    def test_check_fr_is_false(self):
        prod = {}
        api = OpenFoodFactsAPI(1, 1, ["Boissons"])

        is_fr = api._check_product_is_fr(prod)

        self.assertFalse(is_fr, msg="A \"Foreign\" product is taken as a French one.")
