from unittest import mock, skip

from django.test import TestCase, tag
from django.shortcuts import reverse
from django.contrib.messages import get_messages

from users.models import User


class TestUserViews(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(email="oc@oc.com", password="password")

    def setUp(self) -> None:
        patcher = mock.patch("users.views.UserForm")
        self.addCleanup(patcher.stop)
        mock_form_class = patcher.start()
        self.mock_form = mock_form_class.return_value

    # index()
    def test_index_user_is_auth(self):
        self.client.login(email="oc@oc.com", password="password")
        response = self.client.get(reverse("users:index"))

        self.assertRedirects(response, reverse("users:user_account"))

    def test_index_user_not_auth(self):
        response = self.client.get(reverse("users:index"))

        self.assertRedirects(response, reverse("users:user_registration"))

    # user_login()
    def test_user_login(self):
        response = self.client.get(reverse("users:user_login"))

        self.assertTemplateUsed(response, "users/login.html")

    # user_logout()
    def test_user_logout(self):
        self.client.login(email="oc@oc.com", password="password")
        response = self.client.get(reverse("users:user_logout"))

        self.assertRedirects(response, reverse("products:index"))

    # user_check_login()
    def test_user_check_login_form_invalid(self):
        self.mock_form.is_valid.return_value = False
        response = self.client.get(reverse("users:user_check_login"))

        self.assertRedirects(response, reverse("products:index"))

    def test_user_check_login_user_is_valid(self):
        self.mock_form.is_valid.return_value = True
        self.mock_form.cleaned_data = {
            "email": "oc@oc.com",
            "password": "password"
        }

        response = self.client.get(reverse("users:user_check_login"))

        self.assertRedirects(response, reverse("products:index"))

    def test_user_check_login_user_invalid(self):
        self.mock_form.is_valid.return_value = True
        self.mock_form.cleaned_data = {
            "email": "oc@oc.com",
            "password": "WRONG_PASSWORD"
        }

        response = self.client.get(reverse("users:user_check_login"))

        self.assertRedirects(response, reverse("users:user_login"))

    # create_new_user()
    def test_create_new_user(self):
        response = self.client.get(reverse("users:user_registration"))

        self.assertTemplateUsed(response, "users/registration.html")

    # add_new_user()
    def test_add_new_user_form_invalid(self):
        self.mock_form.is_valid.return_value = False

        response = self.client.get(reverse("users:user_add"))
        self.assertRedirects(response, reverse("users:user_registration"))

    def test_add_new_user_ok(self):
        self.mock_form.is_valid.return_value = True
        self.mock_form.cleaned_data = {
            "email": "new_user@oc.com",
            "password": "password"
        }

        response = self.client.get(reverse("users:user_add"))
        users = User.objects.all()

        self.assertEqual(2, len(users))
        self.assertRedirects(response, reverse("users:user_login"))

    def test_add_new_user_already_exists(self):
        self.mock_form.is_valid.return_value = True
        self.mock_form.cleaned_data = {
            "email": "oc@oc.com",
            "password": "password"
        }

        response = self.client.get(reverse("users:user_add"))

        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(1, len(messages))

    # user_account()
    def test_user_account_is_auth(self):
        self.client.login(email="oc@oc.com", password="password")

        response = self.client.get(reverse("users:user_account"))

        self.assertTemplateUsed(response, "users/account.html")

    def test_user_account_anon_user(self):
        response = self.client.get(reverse("users:user_account"))

        self.assertRedirects(response, reverse("users:user_login"))

    # UserManager
    def test_create_user_without_email(self):
        user = {
            "email": "",
            "password": "test"
        }

        with self.assertRaises(ValueError):
            User.objects.create_user(**user)
