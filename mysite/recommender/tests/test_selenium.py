from django.contrib.staticfiles.testing import StaticLiveServerTestCase
# from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from time import sleep


class MySeleniumTests(StaticLiveServerTestCase):
    fixtures = ['genres_selenium.json',
                'actors_selenium.json',
                'movies_selenium.json',
                'users_selenium.json',
                'ratings_selenium.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_register_and_login(self):
        # Register new user
        self.selenium.get(f'{self.live_server_url}')
        self.selenium.find_element_by_xpath('//a[@href="/register/"]').click()
        username_input = self.selenium.find_element_by_xpath('//input[@name="username"]')
        email_input = self.selenium.find_element_by_xpath('//input[@name="email"]')
        password1_input = self.selenium.find_element_by_xpath('//input[@name="password1"]')
        password2_input = self.selenium.find_element_by_xpath('//input[@name="password2"]')
        # Clear each field in case it's pre-populated, send test user's data
        username_input.clear()
        email_input.clear()
        password1_input.clear()
        password2_input.clear()
        username_input.send_keys('testuser')
        email_input.send_keys('testuser@gmail.com')
        password1_input.send_keys('testpassword')
        password2_input.send_keys('testpassword')
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()

        try:
            WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="alert"]'))
            )
            # print(element.get_attribute('innerHTML'))
        except:
            self.assertRaises(TimeoutException)


        print('Account created for' in self.selenium.page_source)
        self.assertTrue('Account created for testuser' in self.selenium.page_source)
        # sleep(5)

        self.selenium.find_element_by_xpath('//a[@href="/login/"]').click()

        try:
            username_input = WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[@name="username"]'))
            )
        except:
            self.assertRaises(TimeoutException)

        # username_input = self.selenium.find_element_by_xpath('//input[@name="username"]')
        username_input.send_keys('testuser')
        password_input = self.selenium.find_element_by_xpath('//input[@name="password"]')
        password_input.send_keys('testpassword')
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()
        self.assertTrue('Logged in as testuser' in self.selenium.page_source)
