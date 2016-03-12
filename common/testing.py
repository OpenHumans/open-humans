import json
import logging
import subprocess

import factory

from django.contrib import auth
from django.db.models import signals
from django.test import LiveServerTestCase, TestCase
from django.test.utils import override_settings

from rest_framework.test import APITestCase as BaseAPITestCase

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions


logger = logging.getLogger(__name__)

UserModel = auth.get_user_model()


@override_settings(SSLIFY_DISABLE=True)
class APITestCase(BaseAPITestCase):
    """
    A helper for writing study tests.
    """

    base_url = ''
    fixtures = ['open_humans/fixtures/test-data.json']

    @factory.django.mute_signals(signals.post_save)
    def verify_request(self, url, method='get', body=None, status=200):
        args = ['/api' + self.base_url + url]

        if method in ['post', 'patch', 'put']:
            args.append(body)

        logger.debug('%s %s', method.upper(), args)

        response = getattr(self.client, method)(*args)

        self.assertEqual(response.status_code, status)

        if method == 'get' and body:
            self.assertEqual(json.loads(response.content), body)

        try:
            return json.loads(response.content)
        except ValueError:
            pass


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

        response = getattr(self.client, method)(url)

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

        for url in self.all_anonymous_urls + self.authenticated_urls:
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
    except:
        return None


class BrowserTestCase(LiveServerTestCase):
    """
    A test case that runs via BrowserStack.
    """

    @classmethod
    def setUpClass(cls):
        super(BrowserTestCase, cls).setUpClass()

        cls.timeout = 10

        cls.driver = webdriver.Chrome()

        cls.driver.maximize_window()
        cls.driver.implicitly_wait(cls.timeout)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

        super(BrowserTestCase, cls).tearDownClass()

    def wait_for_element_id(self, element_id):
        return WebDriverWait(self.driver, self.timeout).until(
            expected_conditions.visibility_of_element_located(
                (By.ID, element_id)))


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
