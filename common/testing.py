import logging
import subprocess

from django.contrib import auth
from django.template import TemplateSyntaxError
from django.test import LiveServerTestCase, TestCase
from django.test.utils import override_settings

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

logger = logging.getLogger(__name__)

UserModel = auth.get_user_model()


@override_settings(SSLIFY_DISABLE=True)
class SmokeTestCase(TestCase):
    """
    A helper for testing lists of URLs.
    """

    fixtures = ['open_humans/fixtures/test-data.json']

    anonymous_urls = []
    authenticated_urls = []
    authenticated_or_anonymous_urls = []
    post_only_urls = []
    redirect_urls = []

    @property
    def all_anonymous_urls(self):
        return self.anonymous_urls + self.authenticated_or_anonymous_urls

    def assert_status_code(self, url, status_code=None, method='get'):
        if not status_code:
            status_code = [200, 302]
        elif isinstance(status_code, int):
            status_code = [status_code]

        try:
            response = getattr(self.client, method)(url)
        except TemplateSyntaxError as e:
            raise Exception('{} had a TemplateSyntaxError: {}'.format(url, e))

        self.assertEqual(
            response.status_code in status_code,
            True,
            msg='{} returned {} instead of {}'.format(
                url, response.status_code, status_code))

    def assert_login(self):
        login = self.client.login(username='beau', password='test')

        self.assertEqual(login, True)

    def test_get_all_simple_urls(self):
        for url in self.all_anonymous_urls:
            self.assert_status_code(url)

    def test_login_redirect(self):
        for url in self.redirect_urls or self.authenticated_urls:
            response = self.client.get(url)

            self.assertRedirects(
                response,
                '/account/login/?next={}'.format(url),
                msg_prefix='{} did not redirect to login URL'.format(url))

    def test_all_urls_with_login(self):
        self.assert_login()

        for url in (self.all_anonymous_urls +
                    self.redirect_urls +
                    self.authenticated_urls):
            self.assert_status_code(url)

    def test_invalid_method(self):
        self.assert_login()

        for url in self.post_only_urls:
            self.assert_status_code(url, status_code=405)

    def test_post_only(self):
        self.assert_login()

        for url in self.post_only_urls:
            self.assert_status_code(url, method='post')


def short_hash():
    """
    Return the current git commit or `None`.
    """
    try:
        return (subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD']).strip())
    except:  # pylint: disable=bare-except
        return None


class BrowserTestCase(LiveServerTestCase):
    """
    A test case that runs via BrowserStack.
    """

    fixtures = ['open_humans/fixtures/test-data.json']

    def setUp(self):
        super(BrowserTestCase, self).setUp()

        self.timeout = 10
        self.driver = webdriver.Chrome()

        self.driver.delete_all_cookies()
        self.driver.maximize_window()

    def tearDown(self):
        self.driver.quit()

        super(BrowserTestCase, self).tearDown()

    def wait_for_element_id(self, element_id):
        return WebDriverWait(self.driver, self.timeout).until(
            expected_conditions.visibility_of_element_located(
                (By.ID, element_id)))

    def login(self):
        driver = self.driver

        driver.get(self.live_server_url + '/account/login/')

        try:
            driver.find_element_by_link_text('Log out').click()
        except NoSuchElementException:
            pass

        username = driver.find_element_by_id('login-username')

        username.clear()
        username.send_keys('beau')

        password = driver.find_element_by_id('login-password')

        password.clear()
        password.send_keys('test')

        driver.find_element_by_id('login').click()

        self.assertEqual(
            'Log out',
            driver.find_element_by_css_selector(
                '.navbar-fixed-top .navbar-right .logout-link').text)

        self.assertEqual(
            'All activities',
            driver.find_element_by_css_selector('.body-main > .container > '
                                                '.row > .toolbar-column '
                                                'button.selected').text)


def get_or_create_user(name):
    """
    Helper to create a Django user.
    """
    try:
        user = UserModel.objects.get(username=name)
    except UserModel.DoesNotExist:
        user = UserModel.objects.create_user(
            name, '{}@test.com'.format(name), name)

    return user
