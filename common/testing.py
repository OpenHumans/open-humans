import json
import logging
import os
import subprocess
import sys
import time

import factory

from django.contrib import auth
from django.db.models import signals
from django.test import LiveServerTestCase, TestCase
from django.test.utils import override_settings

from rest_framework.test import APITestCase as BaseAPITestCase
from selenium import webdriver

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

        cls.capabilities = {
            'browser': 'Chrome',
            'browser_version': '45.0',
            # 'browserstack.debug': True,
            'browserstack.local': True,
            'browserstack.selenium_version': '2.47.1',
            'build': short_hash(),
            'os': 'Windows',
            'os_version': '10',
            'resolution': '1920x1080'
        }

        os_name = 'osx' if sys.platform == 'darwin' else 'linux'

        # Run BrowserStackLocal
        cls.local = subprocess.Popen(
            [
                './bin/BrowserStackLocal-{}'.format(os_name),
                os.getenv('BROWSERSTACK_KEY'),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        # Wait for initialization (could be improved)
        time.sleep(5)

        cls.driver = webdriver.Remote(
            command_executor=os.getenv('BROWSERSTACK_EXECUTOR'),
            desired_capabilities=cls.capabilities)

        cls.driver.maximize_window()

        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

        cls.local.send_signal(subprocess.signal.SIGINT)

        super(BrowserTestCase, cls).tearDownClass()


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
