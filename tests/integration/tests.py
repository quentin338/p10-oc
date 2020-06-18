from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from django.test import LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from users.models import User


chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('window-size=1920x1080')


class AccountTestCase(StaticLiveServerTestCase):
    def setUp(self) -> None:
        self.selenium = webdriver.Chrome(options=chrome_options)
        self.selenium.implicitly_wait(5)
        super(AccountTestCase, self).setUp()
        User.objects.create_user(email="test@test.com", password="Test#2020")

    def tearDown(self) -> None:
        self.selenium.quit()
        super(AccountTestCase, self).tearDown()

    def test_existing_user_can_login(self):
        self.selenium.get(f"{self.live_server_url}/users/login")

        email = self.selenium.find_element_by_id("id_email")
        password = self.selenium.find_element_by_id("id_password")

        self.assertIn("Se connecter", self.selenium.title)

        email.send_keys("test@test.com")
        password.send_keys("Test#2020")

        submit_button = self.selenium.find_element_by_css_selector("input.btn-light")
        submit_button.click()

        self.selenium.find_element_by_class_name("fa-sign-out-alt")

        self.assertIn("users/logout/", self.selenium.page_source)
