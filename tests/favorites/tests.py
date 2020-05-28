import random

from django.test import TestCase
from django.shortcuts import reverse

from model_bakery import baker

from favorites.models import Favorite
from users.models import User


class FavoriteModelTest(TestCase):
    pass


class FavoriteManagerTest(TestCase):
    def setUp(self):
        self.favorite = baker.make("Favorite")

    def test_is_favorite_true(self):
        self.assertTrue(Favorite.objects.is_favorite(self.favorite.user,
                                                     self.favorite.ancient_product,
                                                     self.favorite.new_product))

    def test_is_favorite_false(self):
        self.old_product = baker.make("Product")
        self.assertFalse(Favorite.objects.is_favorite(self.favorite.user,
                                                      self.old_product,
                                                      self.favorite.new_product))


class FavoriteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="oc@oc.com", password="password")
        self.old_product = baker.make("Product", code=random.randint(1, 50000))
        self.new_product = baker.make("Product", code=random.randint(50001, 99999))
        self.favorite = Favorite.objects.create(user=self.user,
                                                ancient_product=self.old_product,
                                                new_product=self.new_product)
        self.client.login(email=self.user.email, password="password")

    # user_favorites_add()
    def test_user_favorites_add(self):
        new_product = baker.make("Product")
        # print("new product code", new_product.code)

        self.client.post(reverse("favorites:user_favorites_add"),
                                    {"old_product_code": self.old_product.code,
                                     "new_product_code": new_product.code})

        self.assertEqual(len(Favorite.objects.all()), 2)

    # user_favorites_delete()
    def test_user_favorites_delete(self):
        self.client.post(reverse("favorites:user_favorites_delete"),
                         {"old_product_code": self.old_product.code,
                          "new_product_code": self.new_product.code})

        self.assertFalse(Favorite.objects.all())

    # show_favorites()
    def test_show_favorites_user_is_logged(self):
        response = self.client.get(reverse("favorites:show_favorites"))
        self.assertTemplateUsed(response, "favorites/show_favorites.html")

    def test_show_favorites_user_is_not_logged(self):
        self.client.logout()

        response = self.client.get(reverse("favorites:show_favorites"))
        self.assertRedirects(response, reverse("users:user_login"))
