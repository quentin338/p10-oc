import os
import json
from unittest import mock, skip

from django.test import TestCase, tag
from django.shortcuts import reverse
from django.contrib.messages import get_messages

from products.models import Product, Category


class ProductModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        path = os.path.dirname(os.path.abspath(__file__))
        sample_file = os.path.join(path, "sample_data", "sample1.json")

        with open(sample_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        cat = Category.objects.create(name="Charcuterie")
        for product in data['products']:
            product['category'] = cat
            Product.objects.create(**product)

    def setUp(self) -> None:
        self.best_prod = Product.objects.get(code=12345)

    def test_retrieving_product_nutriscore_img(self):
        self.assertEqual("nutriscore_a.png", self.best_prod.nutriscore_img)

    def test_retrieving_product_bad_nutriscore_img(self):
        prod_bad = Product.objects.get(code=54321)
        self.assertEqual("nutriscore_d.png", prod_bad.nutriscore_img)

    def test_retrieving_product_nutriscore_full_img(self):
        self.assertEqual("nutriscore_full_a.svg", self.best_prod.nutriscore_full_img)

    def test_retrieving_product_bad_nutriscore_full_img(self):
        prod_bad = Product.objects.get(code=54321)
        self.assertEqual("nutriscore_full_d.svg", prod_bad.nutriscore_full_img)

    def test_retrieving_product_url(self):
        self.assertEqual(f"https://fr.openfoodfacts.org/produit/12345", self.best_prod.url)

    # ProductManager
    def test_search_autocomplete_ten_products(self):
        self.assertEqual(10, len(Product.objects.search_autocomplete("Sauciss")))

    def test_search_autocomplete_order_by_nutriscore_desc(self):
        products = Product.objects.search_autocomplete("Sauciss")
        worst_prod = Product.objects.get(code=98765)
        self.assertEqual(worst_prod.name, products[0], msg="The first product is not the worst")

    def test_better_products_first_six(self):
        product = Product.objects.get(code=98765)
        products = Product.objects.get_better_products(old_product=product)
        self.assertEqual(6, len(products))

    def test_better_products_best_product_first(self):
        product = Product.objects.get(code=98765)
        products = Product.objects.get_better_products(old_product=product)
        self.assertEqual(self.best_prod.code, products[0].code)


class ProductViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cat = Category.objects.create(name="Charcuterie")
        prod = {
            "code": 12345,
            "name": "Saucisson sec",
            "image_url": "http://www.lesaucissonsec.com",
            "nutriscore": 10,
            "nutriscore_grade": "b",
            "ingredients_image": "http://www.stock-image.com/saucisson-sec.jpg",
            "category": cat
        }
        Product.objects.create(**prod)

    # index()
    def test_index_online(self):
        response = self.client.get(reverse('products:index'))
        self.assertEqual(response.status_code, 200)

    def test_index_template_used(self):
        response = self.client.get(reverse('products:index'))
        self.assertTemplateUsed(response, 'products/index.html')

    def test_index_form(self):
        response = self.client.get(reverse('products:index'))
        self.assertHTMLEqual('<tr><th></th><td><input type="text" name="search"'
                             ' class="bg-nav-search search-form" maxlength="100" required id="id_search">'
                             '</td></tr>', str(response.context['form']))

    # product_autocomplete()
    @mock.patch("products.views.Product.objects.search_autocomplete", return_value=["Saucisson"]*10)
    def test_product_autocomplete_return_list(self, autocomplete):

        response = self.client.get(reverse('products:product_autocomplete'), {'term': "saucisson"})

        self.assertEqual(list, type(response.json()))
        self.assertEqual(10, len(response.json()))
        self.assertListEqual(["Saucisson"]*10, response.json())

    def test_product_autocomplete_no_user_search(self):
        with self.assertRaises(ValueError):
            self.client.get(reverse('products:product_autocomplete'))

    # product_search()
    def test_product_search_form_valid(self):
        patcher = mock.patch("products.views.Product.objects.get_better_products")
        mock_user_search = patcher.start()
        mock_user_search.return_value = Product.objects.all()

        with mock.patch('products.views.SearchForm') as MockFormClass:
            mock_form = MockFormClass.return_value
            mock_form.is_valid.return_value = True
            mock_form.cleaned_data = {'search': "Saucisson"}

            response = self.client.get(reverse('products:product_search'))

            self.assertTemplateUsed(response, "products/results.html")
            self.assertEqual(response.context['user_search'], "Saucisson")

    def test_product_search_form_not_valid(self):
        with mock.patch("products.views.SearchForm") as MockFormClass:
            mock_form = MockFormClass.return_value
            mock_form.is_valid.return_value = False

            response = self.client.get(reverse('products:product_search'))

            self.assertRedirects(response, reverse("products:index"))

    def test_product_search_no_old_product(self):
        with mock.patch("products.views.SearchForm") as MockFormClass:
            mock_form = MockFormClass.return_value
            mock_form.is_valid.return_value = True

            response = self.client.get(reverse('products:product_search'))
            messages = [m.message for m in get_messages(response.wsgi_request)]

            self.assertEqual(1, len(messages))
            self.assertRedirects(response, reverse("products:index"))

    # details()
    def test_details_ok_product(self):
        response = self.client.get(reverse("products:product_details", args=[12345]))
        prod = Product.objects.get(code=12345)

        self.assertTemplateUsed(response, "products/details.html")
        self.assertEqual(response.context['product'], prod)

    def test_details_product_does_not_exists(self):
        response = self.client.get(reverse("products:product_details", args=[99999]))

        self.assertRedirects(response, reverse("products:index"))
